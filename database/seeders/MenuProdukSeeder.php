<?php

namespace Database\Seeders;

use App\Models\Kategori;
use App\Models\Produk;
use Illuminate\Database\Seeder;

class MenuProdukSeeder extends Seeder
{
    public function run()
    {
        $menus = [
            'Makanan Utama' => [
                ['name' => 'Indomie Kuah', 'harga' => 8000],
                ['name' => 'Indomie Goreng', 'harga' => 8000],
                ['name' => 'Indomie + Telur', 'harga' => 13000],
                ['name' => 'Chicken Ricebowl Sambal Matah', 'harga' => 15000],
                ['name' => 'Chicken Ricebowl Sambal Bawang', 'harga' => 15000],
                ['name' => 'Chicken Katsu Ricebowl', 'harga' => 15000],
                ['name' => 'Nasi Ayam Goreng Laos', 'harga' => 20000],
            ],
            'Snack / Cemilan' => [
                ['name' => 'Ketan Bubuk', 'harga' => 6000],
                ['name' => 'Pisang Goreng', 'harga' => 10000],
                ['name' => 'Mendoan Banyumas', 'harga' => 10000],
                ['name' => 'Kentang Goreng', 'harga' => 10000],
                ['name' => 'Singkong Goreng', 'harga' => 10000],
                ['name' => 'Roti Maryam', 'harga' => 10000],
                ['name' => 'Tahu Petis', 'harga' => 10000],
                ['name' => 'Cireng', 'harga' => 13000],
                ['name' => 'Azcal Platter', 'harga' => 15000],
                ['name' => 'Pempek Mix / Kapal Selam', 'harga' => 22000],
            ],
            'Minuman' => [
                ['name' => 'Teh Panas', 'harga' => 5000],
                ['name' => 'Es Teh', 'harga' => 7000],
                ['name' => 'Jeruk', 'harga' => 10000],
                ['name' => 'Lemon Tea', 'harga' => 10000],
            ],
            'Milk Based' => [
                ['name' => 'Thai Tea', 'harga' => 13000],
                ['name' => 'Taro', 'harga' => 13000],
                ['name' => 'Avocado', 'harga' => 13000],
                ['name' => 'Bubblegum', 'harga' => 13000],
                ['name' => 'Red Velvet', 'harga' => 13000],
                ['name' => 'Matcha', 'harga' => 15000],
                ['name' => 'Nutella', 'harga' => 15000],
                ['name' => 'Milo', 'harga' => 15000],
            ],
            'Coffee Based' => [
                ['name' => 'Tubruk', 'harga' => 6000],
                ['name' => 'Kopi Susu', 'harga' => 8000],
                ['name' => 'Americano', 'harga' => 10000],
                ['name' => 'Cafe Latte', 'harga' => 15000],
                ['name' => 'Aren Latte', 'harga' => 15000],
                ['name' => 'Cappuccino', 'harga' => 15000],
                ['name' => 'Vanilla Latte', 'harga' => 15000],
                ['name' => 'Butterscotch', 'harga' => 15000],
                ['name' => 'Caramel Latte', 'harga' => 15000],
            ],
            'Add On' => [
                ['name' => 'Telur', 'harga' => 5000],
            ],
        ];

        foreach ($menus as $kategoriName => $products) {
            $kategori = Kategori::firstOrCreate(['name' => $kategoriName]);

            foreach ($products as $product) {
                Produk::updateOrCreate(
                    ['name' => $product['name']],
                    [
                        'kategori_id' => $kategori->id,
                        'harga' => $product['harga'],
                        'stok' => 100,
                        'gambar' => null,
                    ]
                );
            }
        }
    }
}
