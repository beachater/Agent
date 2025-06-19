<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Symfony\Component\Process\Process; // ✅ Add this
use Symfony\Component\Process\Exception\ProcessFailedException;
use Illuminate\Support\Facades\Http;

class TutorController extends Controller
{
    public function showForm()
    {
        return view('tutor');
    }

    public function processForm(Request $request)
    {
        $validated = $request->validate([
            'grade_level' => 'required|string',
            'input_type' => 'required|in:topic,pdf',
            'topic' => 'nullable|string',
            'pdf_path' => 'nullable|string',
            'add_cont' => 'nullable|string',
        ]);

        $python = base_path('storage/app/python/tutor_agent.py');

        $args = [
            'python', $python,
            '--grade_level=' . $validated['grade_level'],
            '--input_type=' . $validated['input_type'],
            '--topic=' . ($validated['topic'] ?? ''),
            '--pdf_path=' . ($validated['pdf_path'] ?? ''),
            '--add_cont=' . ($validated['add_cont'] ?? '')
        ];

        $python = base_path('storage/app/python/tutor_agent.py'); 

        $response = Http::timeout(0)->post('http://192.168.50.127:5001/tutor', [
            'grade_level' => $validated['grade_level'],
            'input_type'  => $validated['input_type'],
            'topic'       => $validated['topic'] ?? '',
            'pdf_path'    => $validated['pdf_path'] ?? '',
            'add_cont'    => $validated['add_cont'] ?? '',
        ]);


        if ($response->failed()) {
            return back()->withErrors(['error' => 'Python API failed.']);
        }

        return view('tutor', ['response' => $response->json()['output'] ?? 'No output received']);
    }
}
    