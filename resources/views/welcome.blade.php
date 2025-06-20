<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Text Rewriter | EduTool</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-gray-100 font-sans text-gray-800 min-h-screen flex items-center justify-center py-12 px-4">

    <div class="w-full max-w-2xl bg-white p-8 rounded-xl shadow-lg">
        <h1 class="text-3xl font-semibold text-center text-gray-800 mb-8">AI Text Leveler</h1>

        {{-- Rewritten Output --}}
        @if (session('rewritten'))
            <div class="mb-6">
                <label class="block font-medium text-gray-700 mb-2">Adaptive Content</label>
                <textarea readonly rows="10"
                    class="w-full p-4 text-sm text-gray-700 bg-gray-50 border border-green-400 rounded-md focus:outline-none">{{ session('rewritten') }}</textarea>
            </div>
        @endif

        {{-- Validation Errors --}}
        @if ($errors->any())
            <div class="mb-6 bg-red-100 text-red-800 p-4 rounded border border-red-300">
                <strong class="block font-medium">Please fix the following:</strong>
                <ul class="list-disc pl-5 mt-2">
                    @foreach ($errors->all() as $error)
                        <li class="text-sm">{{ $error }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <form action="{{ route('rewrite.process') }}" method="POST" enctype="multipart/form-data" class="space-y-6">
            @csrf

            {{-- Input Text --}}
            <div>
                <label for="input_text" class="block text-sm font-medium text-gray-700 mb-1">Enter Text
                    (optional)</label>
                <textarea name="input_text" id="input_text" rows="6"
                    class="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-sm">{{ old('input_text') }}</textarea>
            </div>

            {{-- Upload PDF --}}
            <div>
                <label for="pdf_file" class="block text-sm font-medium text-gray-700 mb-1">Upload PDF (optional)</label>
                <input type="file" name="pdf_file" id="pdf_file" accept=".pdf"
                    class="w-full p-2.5 border border-gray-300 rounded-md text-sm file:mr-4 file:py-2 file:px-4 file:border-0 file:rounded file:bg-indigo-600 file:text-white hover:file:bg-indigo-700 transition" />
            </div>

            {{-- Learner Type --}}
            <div>
                <label for="learner_type" class="block text-sm font-medium text-gray-700 mb-1">Learning Speed</label>
                <select name="learner_type" id="learner_type"
                    class="w-full p-3 border border-gray-300 rounded-md text-sm focus:ring-indigo-500 focus:border-indigo-500"
                    required>
                    <option value="">Select learning speed</option>
                    <option value="slow learner" {{ old('learner_type') == 'slow learner' ? 'selected' : '' }}>Slow
                        Learner</option>
                    <option value="average learner" {{ old('learner_type') == 'average learner' ? 'selected' : '' }}>
                        Average Learner</option>
                    <option value="fast learner" {{ old('learner_type') == 'fast learner' ? 'selected' : '' }}>Fast
                        Learner</option>
                </select>
            </div>

            {{-- Submit Button --}}
            <div class="text-center pt-4">
                <button type="submit"
                    class="bg-indigo-600 text-white font-medium px-6 py-2 rounded-md hover:bg-indigo-700 transition">
                    Generate Adaptive Content
                </button>
            </div>
        </form>
    </div>

</body>

</html>
