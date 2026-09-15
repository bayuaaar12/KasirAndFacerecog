<div class="container-fluid">
    <div class="modern-page-title">
        <div>
            <h1>Dashboard</h1>
            <span>Halo {{ auth()->user()->name }}, selamat datang kembali.</span>
        </div>
        <a href="/admin/transaksi/create" class="btn btn-primary">
            <i class="fas fa-plus mr-1"></i> Transaksi Baru
        </a>
    </div>

    <div class="stat-grid mb-3">
        <div class="stat-card">
            <div class="stat-icon" style="background:#eff6ff;color:#2563eb;">
                <i class="fas fa-cash-register"></i>
            </div>
            <div class="stat-label">Kasir</div>
            <div class="stat-value">Aktif</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:#ecfdf5;color:#0f9f6e;">
                <i class="fas fa-receipt"></i>
            </div>
            <div class="stat-label">Transaksi</div>
            <div class="stat-value">Cepat</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:#fff7ed;color:#d97706;">
                <i class="fas fa-box"></i>
            </div>
            <div class="stat-label">Produk</div>
            <div class="stat-value">Tertata</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background:#fdf2f8;color:#db2777;">
                <i class="fas fa-id-card"></i>
            </div>
            <div class="stat-label">Member</div>
            <div class="stat-value">Siap</div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Akses Cepat</h3>
        </div>
        <div class="card-body">
            <div class="quick-grid">
                <a href="/admin/transaksi" class="quick-link">
                    <i class="fas fa-exchange-alt"></i>
                    Manajemen Transaksi
                </a>
                <a href="/admin/customer" class="quick-link">
                    <i class="fas fa-id-card"></i>
                    Data Customer
                </a>
                <a href="/admin/produk" class="quick-link">
                    <i class="fas fa-table"></i>
                    Data Produk
                </a>
            </div>
        </div>
    </div>
</div>
