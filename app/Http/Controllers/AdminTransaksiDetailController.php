<?php

namespace App\Http\Controllers;

use App\Models\Transaksi;
use App\Models\TransaksiDetail;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Models\Produk;

class AdminTransaksiDetailController extends Controller
{
    //
    function create(Request $request)
    {
        $data = $request->validate([
            'produk_id' => 'required|integer|exists:produks,id',
            'transaksi_id' => 'required|integer|exists:transaksis,id',
            'qty' => 'required|integer|min:1|max:999',
        ]);

        DB::transaction(function () use ($data) {
            $transaksi = Transaksi::lockForUpdate()->findOrFail($data['transaksi_id']);
            abort_if($transaksi->status !== 'pending', 422, 'Transaksi sudah selesai.');
            $produk = Produk::findOrFail($data['produk_id']);
            $td = TransaksiDetail::whereProdukId($produk->id)->whereTransaksiId($transaksi->id)->lockForUpdate()->first();
            $addedSubtotal = $data['qty'] * $produk->harga;

            if ($td) {
                $td->update([
                    'qty' => $td->qty + $data['qty'],
                    'subtotal' => $td->subtotal + $addedSubtotal,
                ]);
            } else {
                TransaksiDetail::create([
                    'produk_id' => $produk->id,
                    'produk_name' => $produk->name,
                    'transaksi_id' => $transaksi->id,
                    'qty' => $data['qty'],
                    'subtotal' => $addedSubtotal,
                ]);
            }

            $transaksi->recalculateTotal();
        });

        $transaksi_id = $data['transaksi_id'];
        return redirect('/admin/transaksi/' . $transaksi_id . '/edit');
    }

    function delete()
    {
        DB::transaction(function () {
            $td = TransaksiDetail::lockForUpdate()->findOrFail(request('id'));
            $transaksi = Transaksi::lockForUpdate()->findOrFail($td->transaksi_id);
            abort_if($transaksi->status !== 'pending', 422, 'Transaksi sudah selesai.');
            $td->delete();
            $transaksi->recalculateTotal();
        });

        return redirect()->back();
    }

    function done($id)
    {
        $transaksi = Transaksi::find($id);
        $data = [
            'status' => 'selesai'
        ];
        $transaksi->update($data);
        return redirect('/admin/transaksi');
    }
}
