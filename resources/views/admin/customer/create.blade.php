<div class="row p-2">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form action="{{ isset($customer) ? '/admin/customer/' . $customer->id : '/admin/customer' }}" method="POST">
                    @csrf
                    @if (isset($customer))
                    @method('PUT')
                    @endif

                    <div class="form-group">
                        <label>Nama Customer</label>
                        <input type="text" name="name" class="form-control" value="{{ old('name', $customer->name ?? '') }}" required>
                    </div>

                    <div class="form-group">
                        <label>No. Telepon</label>
                        <input type="text" name="phone" class="form-control" value="{{ old('phone', $customer->phone ?? '') }}">
                    </div>

                    <div class="form-group">
                        <label>Face Label</label>
                        <input type="text" name="face_label" class="form-control" value="{{ old('face_label', $customer->face_label ?? '') }}" required>
                        <small class="text-muted">Face label harus sama dengan label yang dikirim dari Python.</small>
                    </div>

                    <div class="form-group">
                        <label>Diskon (%)</label>
                        <input type="number" name="discount_percent" min="0" max="100" class="form-control" value="{{ old('discount_percent', $customer->discount_percent ?? 0) }}" required>
                    </div>

                    <div class="form-group">
                        <label>Status Member</label>
                        <select name="is_member" class="form-control" required>
                            <option value="1" {{ old('is_member', $customer->is_member ?? 1) == 1 ? 'selected' : '' }}>Member</option>
                            <option value="0" {{ old('is_member', $customer->is_member ?? 1) == 0 ? 'selected' : '' }}>Bukan Member</option>
                        </select>
                    </div>

                    @if (isset($customer) && $customer->face_image)
                    <div class="form-group">
                        <label>Foto Wajah Tersimpan</label><br>
                        <img src="{{ route('customer.face-image', $customer) }}" alt="{{ $customer->name }}" style="width: 120px; height: 120px; object-fit: cover; border-radius: 8px;">
                    </div>
                    @endif

                    <a href="/admin/customer" class="btn btn-info">Kembali</a>
                    <button type="submit" class="btn btn-primary">Simpan</button>
                </form>
            </div>
        </div>
    </div>
</div>
