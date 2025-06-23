<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\TutorController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/
 

Route::get('/tutor', 'App\Http\Controllers\TutorController@showForm');
Route::post('/tutor', 'App\Http\Controllers\TutorController@processForm');

Route::get('/', function(){
    return view('home');
});


Route::post('/tutor/reset', 'App\Http\Controllers\TutorController@resetConversation');

Route::post('/tutor/followup', [TutorController::class, 'followup']);
