<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class LevelerController extends Controller
{
    public function showForm()
    {
        return view('leveler');
    }

    public function processForm(Request $request)
    {

        set_time_limit(0);
        
        $validated = $request->validate([
            'grade_level' => 'required|string',
            'learning_speed' => 'required|string',
            'input_type' => 'nullable|string',
            'pdf_path' => 'nullable|string',
        ]);

        $python = base_path('storage/app/python/leveler_agent.py');

        $args = [
            'python', $python,
            '--grade-level', $validated['grade_level'],
            '--learning-speed', $validated['learning_speed'],
            '--input-type', $validated['input_type'] ?? '',
            '--pdf-path', $validated['pdf_path'] ?? '',
        ];

        $python = base_path('storage/app/python/tutor_agent.py');

        // Send request to the FastAPI server
        $response = Http::timeout(0)->post('http://192.168.50.144:5001/leveler', [
            'grade_level' => $validated['grade_level'],
            'learning_speed' => $validated['learning_speed'],
            'input_type' => $validated['input_type'] ?? '',
            'pdf_path' => $pdfPath['pdf_path'] ?? '',
        ]);

        if ($response->failed()) {
            return back()->withErrors(['error' => 'Failed to get response from AI service']);
        }

        return view('leveler', ['response' => $response->json()['output'] ?? 'No output']);
    }
}
