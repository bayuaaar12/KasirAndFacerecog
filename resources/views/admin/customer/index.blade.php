<div class="row p-2">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h3 class="card-title">Data Customer</h3>
                <a href="/admin/customer/create" class="btn btn-primary btn-sm"><i class="fas fa-plus"></i> Tambah</a>
            </div>
            <div class="card-body">
                <table class="table table-bordered">
                    <tr>
                        <th>No</th>
                        <th>Nama</th>
                        <th>Telepon</th>
                        <th>Face Label</th>
                        <th>Diskon</th>
                        <th>Member</th>
                        <th>Foto</th>
                        <th>#</th>
                    </tr>
                    @foreach ($customers as $item)
                    <tr>
                        <td>{{ $loop->iteration }}</td>
                        <td>{{ $item->name }}</td>
                        <td>{{ $item->phone }}</td>
                        <td>{{ $item->face_label }}</td>
                        <td>{{ $item->discount_percent }}%</td>
                        <td>{{ $item->is_member ? 'Ya' : 'Tidak' }}</td>
                        <td>
                            @if ($item->face_image)
                            <img src="{{ route('customer.face-image', $item) }}" alt="{{ $item->name }}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;">
                            @else
                            -
                            @endif
                        </td>
                        <td>
                            <a href="/admin/customer/{{ $item->id }}/edit" class="btn btn-info btn-sm"><i class="fas fa-edit"></i></a>
                            <form action="/admin/customer/{{ $item->id }}" method="POST" style="display:inline-block;">
                                @csrf
                                @method('DELETE')
                                <button type="submit" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></button>
                            </form>
                        </td>
                    </tr>
                    @endforeach
                </table>

                <div class="mt-3">
                    {{ $customers->links() }}
                </div>
            </div>
        </div>
    </div>
</div>
