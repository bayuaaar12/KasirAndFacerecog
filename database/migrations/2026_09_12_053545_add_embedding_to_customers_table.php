<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        // [AI/ML INTEGRATION]
        Schema::table('customers', function (Blueprint $table) {
            $table->json('face_embedding')->nullable();
            $table->string('embedding_model')->default('Facenet512');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('customers', function (Blueprint $table) {
            $table->dropColumn(['face_embedding', 'embedding_model']);
        });
    }
};
