<div class="row p-2">

    <div class="col-md-6">
        <div class="card">
            <div class="card-body">

                <div class="row mt-1">
                    <div class="col-md-4">
                        <label for="">Kode Produk</label>
                    </div>
                    <div class="col-md-8">
                        <form method="GET">
                            <div class="d-flex">
                                <select name="produk_id" class="form-control" id="">
                                    <option value="">--{{ isset($p_detail) ? $p_detail->name : 'Nama Produk' }} --</option>
                                    @foreach ($produk as $item)
                                    <option value="{{ $item->id }}">{{ $item->id.' - '. $item->name }}</option>
                                    @endforeach
                                </select>
                                <button type="submit" class="btn btn-primary">Pilih</button>
                            </div>
                        </form>
                    </div>
                </div>

                <form action="/admin/transaksi/detail/create" method="POST">
                    @csrf

                    <input type="hidden" name="transaksi_id" value="{{ Request::segment(3) }}">
                    <input type="hidden" name="produk_id" value="{{ isset($p_detail) ? $p_detail->id : '' }}">

                    <div class="row mt-1">
                        <div class="col-md-4">
                            <label for="">Nama Produk</label>
                        </div>
                        <div class="col-md-8">
                            <input type="text" value="{{ isset($p_detail) ? $p_detail->name : '' }}" class="form-control" disabled name="nama_produk">
                        </div>
                    </div>

                    <div class="row mt-1">
                        <div class="col-md-4">
                            <label for="">Harga Satuan</label>
                        </div>
                        <div class="col-md-8">
                            <input type="text" value="{{ isset($p_detail) ? $p_detail->harga : '' }}" class="form-control" disabled name="harga_satuan">
                        </div>
                    </div>

                    <div class="row mt-1">
                        <div class="col-md-4">
                            <label for="">QTY</label>
                        </div>
                        <div class="col-md-8">
                            <div class="d-flex">
                                <a href="?produk_id={{ request('produk_id') }}&act=min&qty={{ $qty }}" class="btn btn-primary"><i class="fas fa-minus"></i></a>
                                <input type="number" value="{{ $qty }}" id="qty" class="form-control" name="qty">
                                <a href="?produk_id={{ request('produk_id') }}&act=plus&qty={{ $qty }}" class="btn btn-primary"><i class="fas fa-plus"></i></a>
                            </div>
                        </div>
                    </div>

                    <div class="row mt-1">
                        <div class="col-md-4">

                        </div>
                        <div class="col-md-8">
                            <h5>Subtotal : Rp. {{ format_rupiah($subtotal) }}</h5>
                        </div>
                    </div>

                    <div class="row mt-1">
                        <div class="col-md-4">

                        </div>
                        <div class="col-md-8">
                            <a href="/admin/transaksi" class="btn btn-info"><i class="fas fa-arrow-left"></i> Kembali</a>
                            <button type="submit" class="btn btn-primary"> Tambah <i class="fas fa-arrow-right"></i></button>
                        </div>
                    </div>

                </form>

            </div>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <div id="member-detection" class="alert alert-info {{ $transaksi->customer ? '' : 'd-none' }}">
                    @if ($transaksi->customer)
                        <strong>Member diterapkan:</strong> {{ $transaksi->customer->name }}
                        (diskon {{ $transaksi->discount_percent }}%)
                    @else
                        Menunggu deteksi member dari kamera.
                    @endif
                </div>

                @if (!$transaksi->customer)
                    <form id="apply-member-form" action="{{ route('transaksi.member.apply', $transaksi) }}" method="POST" class="d-none mb-3">
                        @csrf
                        <input id="member-detection-id" type="hidden" name="detection_id">
                        <button type="submit" class="btn btn-success btn-sm">Terapkan diskon member</button>
                    </form>
                @endif

                <table class="table">
                    <tr>
                        <th>No</th>
                        <th>Nama Produk</th>
                        <th>QTY</th>
                        <th>Subtotal</th>
                        <th>#</th>
                    </tr>

                    @foreach ($transaksi_detail as $item)
                        
                    <tr>
                        <td>{{ $loop->iteration }}</td>
                        <td>{{ $item->produk_name }}</td>
                        <td>{{ $item->qty }}</td>
                        <td>{{ 'Rp. '.format_rupiah($item->subtotal) }}</td>
                        <td>
                            <a href="/admin/transaksi/detail/delete?id={{ $item->id }}"><i class="fas fa-times"></i></a>
                        </td>
                    </tr>
                    @endforeach
                </table>

                <a href="/admin/transaksi/detail/selesai/{{ Request::segment(3) }}" class="btn btn-success"><i class="fas fa-check"></i> Selesai</a>
                <a href="" class="btn btn-info"><i class="fas fa-file"></i> Pending</a>
            </div>
        </div>
    </div>

</div>

<div class="row p-2">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">

                <form action="" method="GET">
                    <div class="form-group">
                        <label>Subtotal</label>
                        <input type="number" value="{{ $transaksi->subtotal }}" class="form-control" disabled>
                    </div>

                    <div class="form-group">
                        <label>Diskon Member</label>
                        <input type="text" value="{{ $transaksi->discount_percent }}% (Rp. {{ format_rupiah($transaksi->discount_amount) }})" class="form-control" disabled>
                    </div>

                    <div class="form-group">
                        <label>Total Belanja</label>
                        <input type="number" value="{{ $transaksi->total }}" class="form-control" disabled>
                    </div>

                    <div class="form-group">
                        <label for="">Dibayarkan</label>
                        <input type="number" name="dibayarkan" value="{{ request('dibayarkan') }}" class="form-control" id="">
                    </div>

                    <button type="submit" class="btn btn-primary btn-block"> Hitung</button>

                </form>


                <hr>

                <div class="form-group">
                    <label for="">Uang Kembalian</label>
                    <input type="number" value="{{ format_rupiah($kembalian) }}" disabled name="kembalian" class="form-control" id="">
                </div>

                



            </div>
        </div>
    </div>
</div>

<script>
    window.addEventListener('memberDetected', function (event) {
        const member = event.detail;
        const panel = document.getElementById('member-detection');
        const form = document.getElementById('apply-member-form');
        const detectionId = document.getElementById('member-detection-id');

        if (!panel || !form || !detectionId) return;

        panel.classList.remove('d-none');
        panel.innerHTML = '<strong>Member terdeteksi:</strong> ' + member.name +
            ' &mdash; diskon ' + member.discount_percent + '% (score: ' + member.score + ')';
        detectionId.value = member.id;
        form.classList.remove('d-none');
    });
</script>
