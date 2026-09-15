</div>
  <!-- Control Sidebar -->
  <aside class="control-sidebar control-sidebar-dark">
    <!-- Control sidebar content goes here -->
    <div class="p-3">
      <h5>Title</h5>
      <p>Sidebar content</p>
    </div>
  </aside>
  <!-- /.control-sidebar -->

  <!-- Main Footer -->
  <footer class="main-footer">
    <!-- To the right -->
    <div class="float-right d-none d-sm-inline">
      Kasir Pingkal
    </div>
    <!-- Default to the left -->
    <strong>&copy; {{ date('Y') }} Kasir Pingkal.</strong> Semua data toko tersimpan rapi.
  </footer>

</div>
<!-- ./wrapper -->

<!-- REQUIRED SCRIPTS -->

<!-- jQuery -->
<script src="/vendor/admin/plugins/jquery/jquery.min.js"></script>
<!-- Bootstrap 4 -->
<script src="/vendor/admin/plugins/bootstrap/js/bootstrap.bundle.min.js"></script>
<!-- AdminLTE App -->
<script src="/vendor/admin/dist/js/adminlte.min.js"></script>
<script>
  (function () {
    const latestEventKey = 'latest_member_detection_id';
    const pollingPath = '/admin/member-detection/latest';
    const onTransaksiPage = window.location.pathname.indexOf('/admin/transaksi') === 0;

    if (!onTransaksiPage) {
      return;
    }

    async function pollMemberDetection() {
      try {
        const response = await fetch(pollingPath, {
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        if (!response.ok) {
          return;
        }

        const payload = await response.json();
        const event = payload.event;

        if (!event || !event.id) {
          return;
        }

        const latestSeenId = localStorage.getItem(latestEventKey);
        if (latestSeenId === event.id) {
          return;
        }

        localStorage.setItem(latestEventKey, event.id);

        if (typeof Swal !== 'undefined') {
          Swal.fire({
            toast: true,
            position: 'top-end',
            icon: 'success',
            title: 'Pelanggan ini member',
            html: `<b>${event.name}</b><br>Diskon: ${event.discount_percent}%<br>Score: ${event.score}`,
            showConfirmButton: false,
            timer: 5000,
            timerProgressBar: true
          });
        }

        window.dispatchEvent(new CustomEvent('memberDetected', { detail: event }));
      } catch (error) {
      }
    }

    pollMemberDetection();
    setInterval(pollMemberDetection, 3000);
  })();
</script>
</body>
</html>
