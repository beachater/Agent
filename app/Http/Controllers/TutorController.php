<?php

namespace App\Http\Controllers;


use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use App\Models\Conversation;


use GuzzleHttp\Psr7;

class TutorController extends Controller
{
    public function showForm()
    {
        return view('tutor');
    }

    public function resetConversation(Request $request)
{
    $userId = $request->ip();
    Conversation::where('user_identifier', $userId)->delete();
    return redirect('/tutor');
}

    public function followup(Request $request)
{
    try {

        set_time_limit(0);
        
        $request->validate([
            'message' => 'required|string|max:500'
        ]);

        $userId = $request->ip();
        $conversation = Conversation::firstOrCreate(['user_identifier' => $userId]);
        $history = $conversation->history ?? '';
        $userMessage = $request->message;

        $conversationHistory = $history . "\nUser: " . $userMessage;

        $multipartData = [
            ['name' => 'grade_level', 'contents' => 'N/A'],
            ['name' => 'input_type', 'contents' => 'topic'],
            ['name' => 'topic', 'contents' => $userMessage],
            ['name' => 'add_cont', 'contents' => ''],
            ['name' => 'conversation_history', 'contents' => $conversationHistory],
        ];

        $response = Http::timeout(0)
            ->asMultipart()
            ->post('http://192.168.50.127:5001/tutor', $multipartData);

        if ($response->failed()) {
            return response()->json(['error' => 'Python API failed.', 'body' => $response->body()], 500);
        }

        $aiReply = $response->json()['output'] ?? 'No output';

        $conversation->history = $conversationHistory . "\nAI: " . $aiReply;
        $conversation->save();

        return response()->json(['output' => $aiReply]);

    } catch (\Exception $e) {
        return response()->json([
            'error' => 'Internal Server Error',
            'message' => $e->getMessage(),
            'trace' => config('app.debug') ? $e->getTraceAsString() : 'Enable debug mode to view stack trace'
        ], 500);
    }
}



    public function processForm(Request $request)
    {
        set_time_limit(0);

        $validated = $request->validate([
            'grade_level' => 'required|string',
            'input_type' => 'required|in:topic,pdf',
            'topic' => 'nullable|string',
            'pdf_file' => 'nullable|file|mimes:pdf|max:5120',
            'add_cont' => 'nullable|string',
        ]);

        $userId = $request->ip(); // Or use Auth::id() if logged-in users
        $conversation = Conversation::firstOrCreate(
            ['user_identifier' => $userId]
        );

        $conversationHistory = $conversation->history ?? '';
        $userMessage = $validated['topic'] ?? '';

        if ($validated['input_type'] === 'topic' && $userMessage) {
            $conversationHistory .= "\nUser: $userMessage";
        }

        $multipartData = [
            ['name' => 'grade_level', 'contents' => $validated['grade_level']],
            ['name' => 'input_type', 'contents' => $validated['input_type']],
            ['name' => 'topic', 'contents' => $userMessage],
            ['name' => 'add_cont', 'contents' => $validated['add_cont'] ?? ''],
            ['name' => 'conversation_history', 'contents' => $conversationHistory],
        ];

        if ($request->hasFile('pdf_file')) {
            $pdf = $request->file('pdf_file');
            $multipartData[] = [
                'name'     => 'pdf_file',
                'contents' => fopen($pdf->getPathname(), 'r'),
                'filename' => $pdf->getClientOriginalName(),
                'headers'  => [
                    'Content-Type' => $pdf->getMimeType()
                ],
            ];
        }

        $response = Http::timeout(0)
            ->asMultipart()
            ->post('http://192.168.50.127:5001/tutor', $multipartData);

        if ($response->failed()) {
            return back()->withErrors(['error' => 'Python API failed: ' . $response->body()]);
        }

        $aiReply = $response->json()['output'] ?? 'No output';

        if ($validated['input_type'] === 'topic') {
            $conversationHistory .= "\nAI: $aiReply";
            $conversation->history = $conversationHistory;
            $conversation->save();
        }

        return view('tutor', ['response' => $aiReply]);
    }

}


// http://0.0.0.0:5001/tutor