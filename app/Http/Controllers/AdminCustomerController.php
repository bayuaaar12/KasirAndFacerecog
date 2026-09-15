<?php

namespace App\Http\Controllers;

use App\Models\Customer;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use RealRashid\SweetAlert\Facades\Alert;

class AdminCustomerController extends Controller
{
    public function index()
    {
        $data = [
            'title' => 'Manajemen Customer',
            'customers' => Customer::latest()->paginate(10),
            'content' => 'admin/customer/index',
        ];

        return view('admin.layouts.wrapper', $data);
    }

    public function create()
    {
        $data = [
            'title' => 'Tambah Customer',
            'content' => 'admin/customer/create',
        ];

        return view('admin.layouts.wrapper', $data);
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'name' => 'required',
            'phone' => 'nullable',
            'face_label' => 'required|unique:customers,face_label',
            'discount_percent' => 'required|integer|min:0|max:100',
            'is_member' => 'required|boolean',
        ]);

        Customer::create($data);
        Alert::success('Sukses', 'Customer berhasil ditambahkan');

        return redirect('/admin/customer');
    }

    public function show($id)
    {
    }

    public function edit($id)
    {
        $data = [
            'title' => 'Edit Customer',
            'customer' => Customer::findOrFail($id),
            'content' => 'admin/customer/create',
        ];

        return view('admin.layouts.wrapper', $data);
    }

    public function update(Request $request, $id)
    {
        $customer = Customer::findOrFail($id);

        $data = $request->validate([
            'name' => 'required',
            'phone' => 'nullable',
            'face_label' => 'required|unique:customers,face_label,' . $customer->id,
            'discount_percent' => 'required|integer|min:0|max:100',
            'is_member' => 'required|boolean',
        ]);

        $customer->update($data);
        Alert::success('Sukses', 'Customer berhasil diubah');

        return redirect('/admin/customer');
    }

    public function destroy($id)
    {
        $customer = Customer::findOrFail($id);

        if ($customer->face_image && Storage::disk('local')->exists($customer->face_image)) {
            Storage::disk('local')->delete($customer->face_image);
        }

        $customer->delete();
        Alert::success('Sukses', 'Customer berhasil dihapus');

        return redirect()->back();
    }

    public function faceImage(Customer $customer)
    {
        abort_unless($customer->face_image && Storage::disk('local')->exists($customer->face_image), 404);

        return Storage::disk('local')->response($customer->face_image, null, [
            'Cache-Control' => 'private, no-store',
        ]);
    }
}
