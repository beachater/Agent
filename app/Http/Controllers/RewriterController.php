<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class RewriterController extends Controller
{
    public function showForm()
    {
        return view('rewriter');
    }

    public function processForm(Request $request)
{
    set_time_limit(0);

    $validated = $request->validate([
        'learning_speed' => 'required|string',
        'input_text' => 'nullable|string',
        'pdf' => 'nullable|file|mimes:pdf|max:10240',
    ]);

    $pdfPath = '';
    if ($request->hasFile('pdf')) {
        $pdfPath = $request->file('pdf')->storeAs('pdfs', uniqid() . '.pdf');
        $fullPdfPath = storage_path('app/' . $pdfPath);
    }

    $response = Http::timeout(0)->post('http://192.168.50.123:5001/rewriter', [
        'learning_speed' => $validated['learning_speed'],
        'input_type' => $validated['input_text'] ?? '',
        'pdf_path' => $pdfPath['pdf_path'] ?? ''
    ]);

    if ($response->failed()) {
        return back()->withErrors(['error' => 'Python API failed: ' . $response->body()]);
    }

    return view('rewriter', ['response' => $response->json()['output'] ?? 'No output received']);
}
}