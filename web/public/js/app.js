// CineBook - Frontend Application
// Vanilla JS consuming FastAPI backend

const API_BASE = '/api';
let currentUser = null;
let currentShowtimeId = null;
let currentMovie = null;
let allMovies = [];
let allShowtimes = [];
let selectedGenre = 'all';
let searchQuery = '';
let selectedScheduleDate = null;
let seatPollingInterval = null;

let seatData = {
    booked: new Set(),
    held: new Set(),
    mine: new Set()
};
let seats = [];
let ticketToCancel = null;

// ==========================================================================
// UTILITY FUNCTIONS
// ==========================================================================

function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) return;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.role = 'alert';
    alert.innerHTML = `
        <span>${message}</span>
        <button type="button" class="btn-close" aria-label="Close" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(alert);
    setTimeout(() => {
        if (alert.parentNode) alert.remove();
    }, 4500);
}

function formatVND(amount) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
}

function showPage(pageId) {
    document.querySelectorAll('main > section').forEach(s => s.style.display = 'none');
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
    }

    // Update active nav link
    document.querySelectorAll('.cinema-nav-links .nav-link').forEach(link => {
        link.classList.remove('active');
        const navTarget = link.getAttribute('data-nav');
        if (
            (pageId === 'homePage' && navTarget === 'home') ||
            (pageId === 'moviesPage' && navTarget === 'movies') ||
            (pageId === 'schedulePage' && navTarget === 'schedule') ||
            (pageId === 'ticketsPage' && navTarget === 'tickets')
        ) {
            link.classList.add('active');
        }
    });

    // Close mobile nav if open
    const navCollapse = document.getElementById('mainNavbar');
    const toggler = document.getElementById('mobileNavToggler');
    if (navCollapse) navCollapse.classList.remove('show');
    if (toggler) {
        toggler.classList.remove('is-open');
        toggler.setAttribute('aria-expanded', 'false');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleMobileNav() {
    const navCollapse = document.getElementById('mainNavbar');
    const toggler = document.getElementById('mobileNavToggler');
    if (navCollapse) {
        navCollapse.classList.toggle('show');
        const isOpen = navCollapse.classList.contains('show');
        if (toggler) {
            toggler.classList.toggle('is-open', isOpen);
            toggler.setAttribute('aria-expanded', String(isOpen));
        }
    }
}

// ==========================================================================
// API CLIENT
// ==========================================================================

async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include'
    });

    if (response.status === 401) {
        currentUser = null;
        updateAuthUI();
        if (options.requireAuth) {
            openAuthModal('login');
            showAlert('Vui lòng đăng nhập để tiếp tục thao tác.', 'warning');
        }
        return null;
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Lỗi không xác định' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// ==========================================================================
// AUTHENTICATION & MODAL
// ==========================================================================

function updateAuthUI() {
    const userBadge = document.getElementById('userBadge');
    const userName = document.getElementById('userName');
    const loginLink = document.getElementById('loginLink');
    const registerLink = document.getElementById('registerLink');
    const logoutLink = document.getElementById('logoutLink');
    const myTicketsLink = document.getElementById('myTicketsLink');

    if (currentUser) {
        if (userBadge) {
            userBadge.style.display = 'inline-flex';
            if (userName) userName.textContent = currentUser.name || currentUser.username;
        }
        if (loginLink) loginLink.style.display = 'none';
        if (registerLink) registerLink.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'inline-block';
        if (myTicketsLink) myTicketsLink.style.display = 'inline-block';
    } else {
        if (userBadge) userBadge.style.display = 'none';
        if (loginLink) loginLink.style.display = 'inline-block';
        if (registerLink) registerLink.style.display = 'inline-block';
        if (logoutLink) logoutLink.style.display = 'none';
        if (myTicketsLink) myTicketsLink.style.display = 'none';
    }
}

async function checkAuth() {
    try {
        const user = await fetchAPI('/auth/me');
        currentUser = user || null;
    } catch (e) {
        currentUser = null;
    }
    updateAuthUI();
}

function openAuthModal(tab = 'login') {
    const overlay = document.getElementById('authModalOverlay');
    const alertEl = document.getElementById('modalAuthAlert');
    if (alertEl) alertEl.style.display = 'none';
    if (overlay) overlay.style.display = 'flex';
    switchAuthTab(tab);
}

function closeAuthModal() {
    const overlay = document.getElementById('authModalOverlay');
    if (overlay) overlay.style.display = 'none';
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById('modalLoginForm');
    const regForm = document.getElementById('modalRegisterForm');
    const tabLoginBtn = document.getElementById('tabLoginBtn');
    const tabRegBtn = document.getElementById('tabRegisterBtn');
    const alertEl = document.getElementById('modalAuthAlert');
    if (alertEl) alertEl.style.display = 'none';

    if (tab === 'login') {
        if (loginForm) loginForm.style.display = 'block';
        if (regForm) regForm.style.display = 'none';
        if (tabLoginBtn) tabLoginBtn.classList.add('active');
        if (tabRegBtn) tabRegBtn.classList.remove('active');
    } else {
        if (loginForm) loginForm.style.display = 'none';
        if (regForm) regForm.style.display = 'block';
        if (tabLoginBtn) tabLoginBtn.classList.remove('active');
        if (tabRegBtn) tabRegBtn.classList.add('active');
    }
}

function quickFillModalAdmin() {
    const u = document.getElementById('modalLoginUser');
    const p = document.getElementById('modalLoginPass');
    if (u) u.value = 'admin';
    if (p) p.value = '123';
}

function quickFillAdmin() {
    const u = document.getElementById('loginUsername');
    const p = document.getElementById('loginPassword');
    if (u) u.value = 'admin';
    if (p) p.value = '123';
}

async function handleModalLogin(e) {
    if (e) e.preventDefault();
    const u = document.getElementById('modalLoginUser')?.value.trim();
    const p = document.getElementById('modalLoginPass')?.value.trim();
    const alertEl = document.getElementById('modalAuthAlert');

    if (!u || !p) return;

    try {
        const user = await fetchAPI('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username: u, password: p })
        });
        if (user) {
            currentUser = user;
            updateAuthUI();
            closeAuthModal();
            showAlert(`Chào mừng bạn, ${currentUser.name || currentUser.username}! Đăng nhập thành công.`, 'success');
            
            // If user was on booking page, reload booking
            if (currentShowtimeId && document.getElementById('bookingPage').style.display === 'block') {
                loadBookingPage(currentShowtimeId);
            }
        }
    } catch (err) {
        if (alertEl) {
            alertEl.textContent = err.message || 'Tên đăng nhập hoặc mật khẩu không đúng.';
            alertEl.style.display = 'block';
        }
    }
}

async function handleModalRegister(e) {
    if (e) e.preventDefault();
    const u = document.getElementById('modalRegUser')?.value.trim();
    const email = document.getElementById('modalRegEmail')?.value.trim();
    const name = document.getElementById('modalRegName')?.value.trim();
    const p = document.getElementById('modalRegPass')?.value.trim();
    const alertEl = document.getElementById('modalAuthAlert');

    try {
        const user = await fetchAPI('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username: u, email, name, password: p })
        });
        if (user) {
            currentUser = user;
            updateAuthUI();
            closeAuthModal();
            showAlert('Tạo tài khoản thành công! Bạn có thể đặt vé ngay bây giờ.', 'success');
        }
    } catch (err) {
        if (alertEl) {
            alertEl.textContent = err.message || 'Lỗi khi tạo tài khoản.';
            alertEl.style.display = 'block';
        }
    }
}

async function logout() {
    try {
        await fetchAPI('/auth/logout', { method: 'POST' });
    } catch (e) {}
    currentUser = null;
    updateAuthUI();
    showAlert('Đã đăng xuất tài khoản.', 'info');
    showPage('homePage');
}

// ==========================================================================
// MOVIES CATALOG & SEARCH/FILTER
// ==========================================================================

async function loadMovies() {
    try {
        const movies = await fetchAPI('/movies');
        allMovies = movies || [];
        renderHeroSpotlight(allMovies);
        applyMovieFilters();
    } catch (e) {
        showAlert('Không thể tải danh sách phim: ' + e.message, 'danger');
    }
}

function renderHeroSpotlight(movies) {
    if (!movies || movies.length === 0) return;
    
    // Default featured: Oppenheimer or first movie
    const spotlightMovie = movies.find(m => m.title.toLowerCase().includes('oppenheimer')) || movies[0];
    
    const heroTitle = document.getElementById('heroTitle');
    const heroDesc = document.getElementById('heroDesc');
    const heroGenre = document.getElementById('heroGenre');
    const heroDuration = document.getElementById('heroDuration');
    const heroBackdrop = document.getElementById('heroBackdrop');
    const heroBookBtn = document.getElementById('heroBookBtn');
    const heroDetailBtn = document.getElementById('heroDetailBtn');

    if (heroTitle) heroTitle.textContent = spotlightMovie.title;
    if (heroDesc) heroDesc.textContent = spotlightMovie.description;
    if (heroGenre) heroGenre.textContent = spotlightMovie.genre;
    if (heroDuration) heroDuration.textContent = `${spotlightMovie.duration} phút`;
    if (heroBackdrop && spotlightMovie.poster_url) {
        heroBackdrop.style.backgroundImage = `url('${spotlightMovie.poster_url}')`;
    }

    if (heroBookBtn) {
        heroBookBtn.onclick = () => loadMovieDetail(spotlightMovie.id);
    }
    if (heroDetailBtn) {
        heroDetailBtn.onclick = () => loadMovieDetail(spotlightMovie.id);
    }
}

function applyMovieFilters() {
    let filtered = [...allMovies];

    // Filter by genre
    if (selectedGenre && selectedGenre !== 'all') {
        filtered = filtered.filter(m => 
            m.genre.toLowerCase().includes(selectedGenre.toLowerCase())
        );
    }

    // Filter by search query
    if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase().trim();
        filtered = filtered.filter(m => 
            m.title.toLowerCase().includes(q) ||
            (m.director && m.director.toLowerCase().includes(q)) ||
            (m.genre && m.genre.toLowerCase().includes(q))
        );
    }

    renderMoviesGrid('homeMoviesGrid', filtered);
    renderMoviesGrid('moviesGrid', filtered);
}

function renderMoviesGrid(gridId, movies) {
    const grid = document.getElementById(gridId);
    if (!grid) return;

    if (!movies || movies.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px 0;">
                <p style="color: var(--text-muted); font-size: 1.1rem;">Không tìm thấy bộ phim nào phù hợp với từ khóa.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = movies.map(movie => `
        <div class="movie-card" data-movie-id="${movie.id}">
            <div class="movie-poster-wrap">
                <img src="${movie.poster_url || '/images/default.jpg'}" 
                     class="movie-poster" 
                     alt="${movie.title}" 
                     loading="lazy"
                     onerror="this.onerror=null;this.src='/images/default.jpg'">
                <div class="poster-overlay-gradient"></div>
                <div class="movie-duration-tag">${movie.duration} phút</div>
            </div>
            <div class="movie-card-body">
                <div class="movie-card-genre">${movie.genre}</div>
                <h3 class="movie-card-title" title="${movie.title}">${movie.title}</h3>
                <div class="movie-card-director" title="${movie.director}">Đạo diễn: ${movie.director}</div>
                <div class="movie-card-actions">
                    <button type="button" class="card-btn-book" onclick="loadMovieDetail(${movie.id})">
                        Đặt vé
                    </button>
                    <button type="button" class="card-btn-detail" onclick="loadMovieDetail(${movie.id})">
                        Chi tiết
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ==========================================================================
// MOVIE DETAIL PAGE (COMPACT POSTER ON LEFT, INFO & SHOWTIMES ON RIGHT)
// ==========================================================================

async function loadMovieDetail(movieId) {
    try {
        const [movie, showtimes] = await Promise.all([
            fetchAPI(`/movies/${movieId}`),
            fetchAPI(`/movies/${movieId}/showtimes`)
        ]);

        currentMovie = movie;

        const posterEl = document.getElementById('moviePoster');
        if (posterEl) {
            posterEl.src = movie.poster_url || '/images/default.jpg';
            posterEl.alt = movie.title;
        }

        document.getElementById('movieTitle').textContent = movie.title;
        document.getElementById('movieGenre').textContent = movie.genre;
        document.getElementById('movieDuration').textContent = movie.duration;
        document.getElementById('movieDirector').textContent = movie.director;
        document.getElementById('movieReleaseDate').textContent = new Date(movie.release_date).toLocaleDateString('vi-VN');
        document.getElementById('movieDescription').textContent = movie.description;

        const breadcrumb = document.getElementById('detailBreadcrumb');
        if (breadcrumb) breadcrumb.textContent = `Trang chủ / Chi tiết phim: ${movie.title}`;

        renderMovieDetailShowtimes(showtimes);
        showPage('movieDetailPage');
    } catch (e) {
        showAlert('Không thể tải chi tiết phim: ' + e.message, 'danger');
    }
}

function renderMovieDetailShowtimes(showtimes) {
    const container = document.getElementById('showtimesContainer');
    if (!container) return;

    if (!showtimes || showtimes.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.95rem;">Hiện chưa có suất chiếu nào cho bộ phim này.</p>';
        return;
    }

    container.innerHTML = showtimes.map(st => {
        const dateStr = new Date(st.start_time).toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit' });
        const timeStr = new Date(st.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        return `
            <div class="detail-showtime-item">
                <div class="detail-showtime-info">
                    <div class="st-time">${timeStr} <span class="st-date-badge">${dateStr}</span></div>
                    <div class="st-room">${st.room_name || 'Phòng chiếu tiêu chuẩn'}</div>
                </div>
                <button type="button" class="btn btn-cinema btn-sm" onclick="loadBookingPage(${st.id})">
                    Chọn ghế
                </button>
            </div>
        `;
    }).join('');
}

// ==========================================================================
// SCHEDULE PAGE
// ==========================================================================

async function loadSchedule() {
    showPage('schedulePage');
    try {
        const showtimes = await fetchAPI('/showtimes');
        allShowtimes = showtimes || [];
        renderScheduleDateTabs();
        renderScheduleList();
    } catch (e) {
        showAlert('Không thể tải lịch chiếu: ' + e.message, 'danger');
    }
}

function renderScheduleDateTabs() {
    const container = document.getElementById('scheduleDateTabs');
    if (!container) return;

    const days = [];
    const today = new Date();

    for (let i = 0; i < 5; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() + i);
        const dateKey = d.toISOString().split('T')[0];
        
        let label = '';
        if (i === 0) label = 'Hôm nay';
        else if (i === 1) label = 'Ngày mai';
        else {
            const dayNames = ['CN', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
            label = dayNames[d.getDay()];
        }

        const dateStr = `${d.getDate()}/${d.getMonth() + 1}`;
        days.push({ key: dateKey, label, dateStr });
    }

    if (!selectedScheduleDate) {
        selectedScheduleDate = days[0].key;
    }

    container.innerHTML = days.map(day => `
        <button type="button" class="date-tab-btn ${day.key === selectedScheduleDate ? 'active' : ''}" 
                onclick="selectScheduleDate('${day.key}')">
            <span class="date-tab-day">${day.label}</span>
            <span class="date-tab-date">${day.dateStr}</span>
        </button>
    `).join('');
}

function selectScheduleDate(dateKey) {
    selectedScheduleDate = dateKey;
    renderScheduleDateTabs();
    renderScheduleList();
}

function renderScheduleList() {
    const listContainer = document.getElementById('scheduleList');
    if (!listContainer) return;

    const dateShowtimes = allShowtimes.filter(st => {
        const stDate = new Date(st.start_time).toISOString().split('T')[0];
        return stDate === selectedScheduleDate;
    });

    if (dateShowtimes.length === 0) {
        listContainer.innerHTML = `
            <div style="text-align: center; padding: 40px 0;">
                <p style="color: var(--text-muted); font-size: 1.05rem;">Chưa có suất chiếu nào được lên lịch cho ngày này.</p>
            </div>
        `;
        return;
    }

    const groupedByMovie = {};
    dateShowtimes.forEach(st => {
        if (!groupedByMovie[st.movie_id]) {
            groupedByMovie[st.movie_id] = {
                movieId: st.movie_id,
                title: st.movie_title || 'Phim',
                poster: st.movie_poster_url || '/images/default.jpg',
                duration: st.movie_duration || 120,
                genre: st.movie_genre || 'Chiếu rạp',
                showtimes: []
            };
        }
        groupedByMovie[st.movie_id].showtimes.push(st);
    });

    listContainer.innerHTML = Object.values(groupedByMovie).map(group => `
        <div class="schedule-movie-row">
            <img src="${group.poster}" 
                 class="schedule-movie-thumb" 
                 alt="${group.title}" 
                 onerror="this.onerror=null;this.src='/images/default.jpg'">
            <div class="schedule-movie-info">
                <h3 class="schedule-movie-title">${group.title}</h3>
                <div class="schedule-movie-meta">
                    <span>${group.genre}</span>
                    <span>⏱️ ${group.duration} phút</span>
                </div>
                <div class="schedule-chips-container">
                    ${group.showtimes.map(st => {
                        const time = new Date(st.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                        return `
                            <div class="showtime-chip" onclick="loadBookingPage(${st.id})">
                                <span class="showtime-chip-time">${time}</span>
                                <span class="showtime-chip-room">${st.room_name || 'Phòng chiếu'}</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

// ==========================================================================
// BOOKING PAGE & SEAT SELECTION
// ==========================================================================

async function loadBookingPage(showtimeId) {
    if (!currentUser) {
        showAlert('Vui lòng đăng nhập để tiến hành đặt ghế.', 'warning');
        currentShowtimeId = showtimeId;
        openAuthModal('login');
        return;
    }

    currentShowtimeId = showtimeId;
    try {
        const [showtime, snapshot] = await Promise.all([
            fetchAPI(`/showtimes/${showtimeId}`),
            fetchAPI(`/showtimes/${showtimeId}/seats`)
        ]);

        document.getElementById('bookingMovieTitle').textContent = showtime.movie_title || 'Đặt vé xem phim';
        
        const stDate = new Date(showtime.start_time).toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' });
        const stTime = new Date(showtime.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        document.getElementById('bookingSubtitle').textContent = `${stDate} · Giờ chiếu: ${stTime}`;

        const roomPill = document.getElementById('bookingRoomPill');
        if (roomPill) roomPill.textContent = showtime.room_name || 'Phòng chiếu tiêu chuẩn';

        renderSeats(snapshot);
        updateBookingSummary();
        showPage('bookingPage');
        setupLiveSeatSync(showtimeId);
    } catch (e) {
        showAlert('Không thể tải trang đặt vé: ' + e.message, 'danger');
    }
}

function goBackFromBooking() {
    if (currentMovie && currentMovie.id) {
        loadMovieDetail(currentMovie.id);
    } else {
        showPage('homePage');
    }
}

function renderSeats(snapshot) {
    seatData = {
        booked: new Set(snapshot.booked || []),
        held: new Set(snapshot.held || []),
        mine: new Set(snapshot.mine || [])
    };

    const grid = document.getElementById('cinemaSeatGrid');
    if (!snapshot.seats || snapshot.seats.length === 0) {
        grid.innerHTML = '<p style="color: var(--text-muted);">Phòng chiếu này chưa được cấu hình sơ đồ ghế.</p>';
        return;
    }

    seats = snapshot.seats;
    
    // Calculate columns per row based on capacity
    const capacity = seats.length;
    let cols = 6;
    if (capacity % 5 === 0 && capacity <= 20) cols = 5;
    else if (capacity % 4 === 0 && capacity <= 16) cols = 4;

    const rowMap = {};
    seats.forEach((seat) => {
        const rowIndex = Math.floor((seat.number - 1) / cols);
        const colIndex = ((seat.number - 1) % cols) + 1;
        const rowLetter = String.fromCharCode(65 + rowIndex); // A, B, C, D...
        const seatCode = `${rowLetter}${colIndex}`;
        
        if (!rowMap[rowLetter]) rowMap[rowLetter] = [];
        rowMap[rowLetter].push({ ...seat, seatCode, isVip: rowIndex >= 2 });
    });

    grid.innerHTML = Object.keys(rowMap).map(rowLetter => `
        <div class="seat-row">
            <div class="seat-row-label">${rowLetter}</div>
            <div class="seat-row-seats">
                ${rowMap[rowLetter].map(seat => {
                    let statusClass = '';
                    let isDisabled = false;

                    if (seatData.booked.has(seat.id)) {
                        statusClass = 'booked';
                        isDisabled = true;
                    } else if (seatData.mine.has(seat.id)) {
                        statusClass = 'mine';
                    } else if (seatData.held.has(seat.id)) {
                        statusClass = 'holding';
                        isDisabled = true;
                    } else if (seat.isVip) {
                        statusClass = 'vip-seat';
                    }

                    return `
                        <button type="button"
                                class="live-seat ${statusClass}"
                                id="seat-btn-${seat.id}"
                                data-seat-id="${seat.id}"
                                data-seat-code="${seat.seatCode}"
                                ${isDisabled ? 'disabled' : ''}
                                onclick="toggleSeat(${seat.id}, '${seat.seatCode}')"
                                title="Ghế ${seat.seatCode} ${seat.isVip ? '(VIP)' : ''}">
                            <span class="seat-back">${seat.seatCode}</span>
                            <span class="seat-base"></span>
                        </button>
                    `;
                }).join('')}
            </div>
            <div class="seat-row-label">${rowLetter}</div>
        </div>
    `).join('');
}

async function toggleSeat(seatId, seatCode) {
    if (!currentShowtimeId) return;

    if (seatData.booked.has(seatId) || seatData.held.has(seatId)) {
        return;
    }

    const action = seatData.mine.has(seatId) ? 'release' : 'hold';

    try {
        const result = await fetchAPI(`/showtimes/${currentShowtimeId}/seat-action`, {
            method: 'POST',
            body: JSON.stringify({ action, seat_id: seatId })
        });

        if (result && result.ok) {
            if (action === 'hold') {
                seatData.mine.add(seatId);
            } else {
                seatData.mine.delete(seatId);
            }
            updateSeatElementState(seatId);
            updateBookingSummary();
        } else {
            showAlert(result?.message || 'Không thể chọn ghế này.', 'warning');
        }
    } catch (e) {
        showAlert('Lỗi khi giữ ghế: ' + e.message, 'danger');
    }
}

function updateSeatElementState(seatId) {
    const btn = document.getElementById(`seat-btn-${seatId}`);
    if (!btn) return;

    btn.classList.remove('mine', 'holding', 'booked');
    if (seatData.booked.has(seatId)) {
        btn.classList.add('booked');
        btn.disabled = true;
    } else if (seatData.mine.has(seatId)) {
        btn.classList.add('mine');
        btn.disabled = false;
    } else if (seatData.held.has(seatId)) {
        btn.classList.add('holding');
        btn.disabled = true;
    } else {
        btn.disabled = false;
    }
}

function updateBookingSummary() {
    const selectedCount = seatData.mine.size;
    const ticketSelect = document.getElementById('ticketType');
    const unitPrice = ticketSelect?.value === 'Child' ? 50000 : 100000;
    const totalPrice = selectedCount * unitPrice;

    // Selected seat names
    const namesEl = document.getElementById('selectedSeatNames');
    if (namesEl) {
        if (selectedCount === 0) {
            namesEl.textContent = 'Chưa chọn';
        } else {
            const chosenCodes = [];
            seatData.mine.forEach(id => {
                const btn = document.getElementById(`seat-btn-${id}`);
                if (btn) chosenCodes.push(btn.getAttribute('data-seat-code'));
            });
            namesEl.textContent = chosenCodes.join(', ');
        }
    }

    // Selected count
    const countEl = document.getElementById('selectedSeatCount');
    if (countEl) countEl.textContent = `${selectedCount} vé`;

    // Total price
    const priceEl = document.getElementById('totalPriceDisplay');
    if (priceEl) priceEl.textContent = formatVND(totalPrice);

    // Book now button
    const bookBtn = document.getElementById('bookNowButton');
    if (bookBtn) {
        bookBtn.disabled = selectedCount === 0;
    }
}

function setupLiveSeatSync(showtimeId) {
    if (seatPollingInterval) clearInterval(seatPollingInterval);
    
    // Heartbeat & polling every 4 seconds to sync holds with server
    seatPollingInterval = setInterval(async () => {
        if (!currentShowtimeId || document.getElementById('bookingPage').style.display === 'none') {
            clearInterval(seatPollingInterval);
            return;
        }

        try {
            // Heartbeat for our held seats
            if (seatData.mine.size > 0) {
                await fetchAPI(`/showtimes/${showtimeId}/seat-action`, {
                    method: 'POST',
                    body: JSON.stringify({ action: 'heartbeat' })
                });
            }

            // Fetch latest snapshot
            const snapshot = await fetchAPI(`/showtimes/${showtimeId}/seats`);
            if (snapshot) {
                seatData.booked = new Set(snapshot.booked || []);
                seatData.held = new Set(snapshot.held || []);
                snapshot.seats?.forEach(s => updateSeatElementState(s.id));
                updateBookingSummary();
            }
        } catch (e) {}
    }, 4000);
}

// Execute Booking action
async function executeBooking() {
    if (!currentShowtimeId || seatData.mine.size === 0) {
        showAlert('Vui lòng chọn ít nhất 1 ghế để tiếp tục.', 'warning');
        return;
    }

    if (!currentUser) {
        openAuthModal('login');
        showAlert('Vui lòng đăng nhập để hoàn tất đặt vé.', 'warning');
        return;
    }

    const ticketType = document.getElementById('ticketType')?.value || 'Adult';
    const bookBtn = document.getElementById('bookNowButton');
    if (bookBtn) {
        bookBtn.disabled = true;
        bookBtn.textContent = 'Đang xử lý đặt vé...';
    }

    try {
        const result = await fetchAPI(`/showtimes/${currentShowtimeId}/book`, {
            method: 'POST',
            body: JSON.stringify({ ticket_type: ticketType })
        });

        if (result && result.tickets) {
            showAlert(`Đặt vé thành công! Bạn đã đặt ${result.tickets.length} vé.`, 'success');
            seatData.mine.clear();
            if (seatPollingInterval) clearInterval(seatPollingInterval);
            loadMyTickets();
        } else {
            showAlert('Đặt vé không thành công, vui lòng thử lại.', 'danger');
        }
    } catch (e) {
        showAlert('Lỗi khi xác nhận đặt vé: ' + e.message, 'danger');
    } finally {
        if (bookBtn) {
            bookBtn.disabled = false;
            bookBtn.textContent = 'Xác nhận đặt vé';
        }
    }
}

// Ticket type change recalculates price
document.getElementById('ticketType')?.addEventListener('change', updateBookingSummary);

// ==========================================================================
// MY TICKETS PAGE
// ==========================================================================

async function loadMyTickets() {
    if (!currentUser) {
        showAlert('Vui lòng đăng nhập để xem vé của bạn.', 'warning');
        openAuthModal('login');
        return;
    }

    showPage('ticketsPage');
    try {
        const tickets = await fetchAPI('/tickets');
        renderMyTickets(tickets);
    } catch (e) {
        showAlert('Không thể tải danh sách vé: ' + e.message, 'danger');
    }
}

function renderMyTickets(tickets) {
    const grid = document.getElementById('ticketsGrid');
    if (!grid) return;

    if (!tickets || tickets.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px 0;">
                <p style="color: var(--text-muted); font-size: 1.1rem;">Bạn chưa đặt vé nào trong hệ thống.</p>
                <button type="button" class="btn btn-cinema" style="margin-top: 14px;" onclick="showPage('homePage')">
                    Khám phá phim đang chiếu
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = tickets.map(t => {
        const dateStr = new Date(t.start_time).toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' });
        const timeStr = new Date(t.start_time).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        
        // Calculate seat code
        const seatNum = t.seat_number || 1;
        const rowLetter = String.fromCharCode(65 + Math.floor((seatNum - 1) / 6));
        const colNum = ((seatNum - 1) % 6) + 1;
        const seatCode = `${rowLetter}${colNum}`;

        return `
            <div class="ticket-stub-card" id="ticket-card-${t.id}">
                <div class="ticket-stub-header">
                    <span class="ticket-id-tag">MÃ VÉ: #CB-${t.id.toString().padStart(5, '0')}</span>
                    <span class="ticket-status-badge">ĐÃ XÁC NHẬN</span>
                </div>
                <div class="ticket-stub-body">
                    <img src="/images/default.jpg" class="ticket-movie-thumb" alt="${t.movie_title}">
                    <div class="ticket-details">
                        <h4 class="ticket-movie-title">${t.movie_title}</h4>
                        <div class="ticket-info-item">🎬 Phòng: <strong>${t.room_name}</strong></div>
                        <div class="ticket-info-item">📅 Suất: <strong>${timeStr} · ${dateStr}</strong></div>
                        <div class="ticket-info-item">💺 Ghế: <strong>${seatCode}</strong> (${t.ticket_type === 'Child' ? 'Trẻ em' : 'Người lớn'})</div>
                    </div>
                </div>
                <div class="ticket-stub-perforation"></div>
                <div class="ticket-stub-footer">
                    <div class="ticket-price-box">${formatVND(t.price)}</div>
                    <button type="button" class="ticket-cancel-btn" onclick="openCancelModal(${t.id}, '${t.movie_title}', '${seatCode}')">
                        Hủy vé
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function openCancelModal(ticketId, movieTitle, seatCode) {
    ticketToCancel = ticketId;
    const modal = document.getElementById('cancelConfirmOverlay');
    const textEl = document.getElementById('cancelConfirmText');
    if (textEl) {
        textEl.textContent = `Bạn có chắc chắn muốn hủy vé phim "${movieTitle}" (Ghế ${seatCode}) không? Chỗ ngồi sẽ được trả lại cho phòng chiếu.`;
    }
    if (modal) modal.style.display = 'flex';
}

function closeCancelModal() {
    ticketToCancel = null;
    const modal = document.getElementById('cancelConfirmOverlay');
    if (modal) modal.style.display = 'none';
}

async function executeCancelTicket() {
    if (!ticketToCancel) return;

    try {
        const result = await fetchAPI(`/tickets/${ticketToCancel}`, { method: 'DELETE' });
        if (result) {
            showAlert('Đã hủy vé thành công.', 'success');
            closeCancelModal();
            loadMyTickets();
        }
    } catch (e) {
        showAlert('Không thể hủy vé: ' + e.message, 'danger');
    }
}

// ==========================================================================
// SEARCH & FILTER EVENT LISTENERS
// ==========================================================================

function setupFilterEvents() {
    const searchInput = document.getElementById('movieSearchInput');
    const clearBtn = document.getElementById('clearSearchBtn');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value;
            if (clearBtn) clearBtn.style.display = searchQuery ? 'block' : 'none';
            applyMovieFilters();
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            searchQuery = '';
            clearBtn.style.display = 'none';
            applyMovieFilters();
        });
    }

    // Genre buttons on Home and Movies Page
    document.querySelectorAll('.genre-pill').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.genre-pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedGenre = btn.getAttribute('data-genre') || 'all';
            applyMovieFilters();
        });
    });
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    loadMovies();
    setupFilterEvents();

    // Close auth modal on backdrop click
    const authOverlay = document.getElementById('authModalOverlay');
    if (authOverlay) {
        authOverlay.addEventListener('click', (e) => {
            if (e.target === authOverlay) closeAuthModal();
        });
    }

    // Close cancel modal on backdrop click
    const cancelOverlay = document.getElementById('cancelConfirmOverlay');
    if (cancelOverlay) {
        cancelOverlay.addEventListener('click', (e) => {
            if (e.target === cancelOverlay) closeCancelModal();
        });
    }

    // Release held seats when page unloads
    window.addEventListener('pagehide', () => {
        if (currentShowtimeId && seatData.mine.size > 0) {
            navigator.sendBeacon(
                `${API_BASE}/showtimes/${currentShowtimeId}/seat-action`,
                JSON.stringify({ action: 'release_all' })
            );
        }
        if (seatPollingInterval) clearInterval(seatPollingInterval);
    });
});