<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('member_detections', function (Blueprint $table) {
            $table->id();
            $table->uuid('event_uuid')->unique();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->foreignId('transaksi_id')->nullable()->constrained('transaksis')->nullOnDelete();
            $table->decimal('score', 5, 4);
            $table->boolean('liveness_passed');
            // datetime keeps this migration compatible with older MySQL versions.
            $table->dateTime('detected_at');
            $table->dateTime('expires_at');
            $table->dateTime('applied_at')->nullable();
            $table->timestamps();

            $table->index(['applied_at', 'expires_at']);
        });
    }

    public function down()
    {
        Schema::dropIfExists('member_detections');
    }
};
