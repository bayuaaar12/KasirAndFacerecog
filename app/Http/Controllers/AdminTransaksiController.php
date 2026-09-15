<?php

namespace App\Http\Controllers;

use App\Models\Produk;
use App\Models\Transaksi;
use App\Models\TransaksiDetail;
use App\Models\MemberDetection;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use RealRashid\SweetAlert\Facades\Alert;

// [LOGIKA BISNIS / NON-AI]
class AdminTransaksiController extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function index()
    {
        //
        $data = [
            'title'     => 'Manajemen Transaksi',
            'transaksi'  => Transaksi::orderBy('created_at', 'DESC')->paginate(10),
            'content'   => 'admin/transaksi/index'
        ];
        return view('admin.layouts.wrapper', $data);
    }

    /**
     * Show the form for creating a new resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function create()
    {
        //
        $data = [
            'user_id'   => auth()->user()->id,
            'kasir_name'   => auth()->user()->name,
            'total'     => 0
        ];
        $transaksi = Transaksi::create($data);
        return redirect('/admin/transaksi/' . $transaksi->id . '/edit');
    }



    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function show($id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function edit($id)
    {
        //
        $produk = Produk::get();

        $produk_id = request('produk_id');
        $p_detail = Produk::find($produk_id);

        $transaksi_detail = TransaksiDetail::whereTransaksiId($id)->get();

        $act = request('act');
        $qty = request('qty');
        if ($act == 'min') {
            if ($qty <= 1) {
                $qty = 1;
            } else {
                $qty = $qty - 1;
            }
        } else {
            $qty = $qty + 1;
        }

        $subtotal = 0;
        if ($p_detail) {
            $subtotal = $qty * $p_detail->harga;
        }

        $transaksi = Transaksi::find($id);

        $dibayarkan = request('dibayarkan');
        $kembalian = $dibayarkan - $transaksi->total;



        $data = [
            'title'     => 'Tambah Transaksi',
            'produk'    => $produk,
            'p_detail'  => $p_detail,
            'qty'       => $qty,
            'subtotal'       => $subtotal,
            'transaksi_detail'       => $transaksi_detail,
            'transaksi' => $transaksi,
            'kembalian' => $kembalian,
            'content'   => 'admin/transaksi/create'
        ];
        return view('admin.layouts.wrapper', $data);
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, $id)
    {
        //
    }

    public function applyMember(Request $request, Transaksi $transaksi)
    {
        $data = $request->validate([
            'detection_id' => 'required|integer',
        ]);

        if ($transaksi->status !== 'pending') {
            return redirect()->back()->withErrors(['member' => 'Member hanya dapat diterapkan pada transaksi pending.']);
        }

        DB::transaction(function () use ($data, $transaksi) {
            $detection = MemberDetection::query()
                ->with('customer')
                ->lockForUpdate()
                ->findOrFail($data['detection_id']);

            if ($detection->applied_at || $detection->expires_at->isPast() || !$detection->customer->is_member) {
                abort(422, 'Deteksi member sudah kedaluwarsa atau telah digunakan.');
            }

            $transaksi->update([
                'customer_id' => $detection->customer_id,
                'discount_percent' => $detection->customer->discount_percent,
            ]);
            $transaksi->recalculateTotal();

            $detection->update([
                'transaksi_id' => $transaksi->id,
                'applied_at' => now(),
            ]);
        });

        Alert::success('Member diterapkan', 'Diskon member sudah diterapkan ke transaksi.');

        return redirect('/admin/transaksi/' . $transaksi->id . '/edit');
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  int  $id
     * @return \Illuminate\Http\Response
     */
    public function destroy($id)
    {
        $transaksi = Transaksi::find($id);

        if (!$transaksi) {
            Alert::error('Gagal', 'Transaksi tidak ditemukan');
            return redirect()->back();
        }

        TransaksiDetail::whereTransaksiId($id)->delete();
        $transaksi->delete();

        Alert::success('Sukses', 'Transaksi berhasil dihapus');
        return redirect()->back();
    }
}
