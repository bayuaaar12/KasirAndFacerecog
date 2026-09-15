<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::table('transaksis', function (Blueprint $table) {
            $table->foreignId('customer_id')->nullable()->after('user_id')->constrained('customers')->nullOnDelete();
            $table->unsignedBigInteger('subtotal')->default(0)->after('total');
            $table->unsignedInteger('discount_percent')->default(0)->after('subtotal');
            $table->unsignedBigInteger('discount_amount')->default(0)->after('discount_percent');
        });

        // Existing transactions stored their pre-discount amount in total.
        DB::table('transaksis')->update(['subtotal' => DB::raw('total')]);
    }

    public function down()
    {
        Schema::table('transaksis', function (Blueprint $table) {
            $table->dropConstrainedForeignId('customer_id');
            $table->dropColumn(['subtotal', 'discount_percent', 'discount_amount']);
        });
    }
};
