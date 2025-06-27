<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProofreaderController;
use App\Http\Controllers\FiveQuestionsController;
use App\Http\Controllers\RealWorldController;
use App\Http\Controllers\SentenceStarterController;
use App\Http\Controllers\TranslatorController;
use App\Http\Controllers\StudyHabitsController;
/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
| These routes handle your AI agents and tools.
|--------------------------------------------------------------------------
*/

//  Optional: Redirect homepage to 5 Questions tool
Route::get('/', function () {
    return redirect()->route('fivequestions.form');
});

//  5 Questions Agent
Route::get('/5questions', [FiveQuestionsController::class, 'showForm'])->name('fivequestions.form');
Route::post('/5questions', [FiveQuestionsController::class, 'processForm'])->name('fivequestions.process');

// Proofreader Agent 
Route::get('/proofreader', [ProofreaderController::class, 'showForm'])->name('proofreader.form');
Route::post('/proofreader', [ProofreaderController::class, 'processForm'])->name('proofreader.process');

// Real World Agent
Route::get('/realworld', [RealWorldController::class, 'showForm'])->name('realworld.form');
Route::post('/realworld', [RealWorldController::class, 'processForm'])->name('realworld.process');

// Sentence Starter Agent
Route::get('/sentencestarter', [SentenceStarterController::class, 'showForm'])->name('sentencestarter.form');
Route::post('/sentencestarter', [SentenceStarterController::class, 'processForm'])->name('sentencestarter.process');

// Translator Agent
Route::get('/translator', [TranslatorController::class, 'showForm'])->name('translator.form');
Route::post('/translator', [TranslatorController::class, 'processForm'])->name('translator.process');

// Study Habits Agent
Route::get('/studyhabits', [StudyHabitsController::class, 'showForm'])->name('studyhabits.form');
Route::post('/studyhabits', [StudyHabitsController::class, 'processForm'])->name('studyhabits.process');
