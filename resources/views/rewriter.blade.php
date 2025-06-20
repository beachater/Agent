<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AI Text Rewriter</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous" />
    <style>
        body {
            background: linear-gradient(to right, #ffe6ec, #ffffff);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #2c2c2c;
            padding: 4rem 1rem;
        }

        .container {
            background: #ffffff;
            max-width: 720px;
            padding: 3rem 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        }

        h2 {
            font-weight: 800;
            font-size: 2rem;
            text-align: center;
            color: #e91e63;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            text-align: center;
            font-size: 1rem;
            margin-bottom: 2rem;
            color: #555;
        }

        label {
            font-weight: 600;
            color: #2c2c2c;
        }

        .form-control,
        .form-select {
            border-radius: 10px;
            font-size: 1rem;
            color: #2c2c2c;
        }

        .form-control:focus,
        .form-select:focus {
            border-color: #e91e63;
            box-shadow: 0 0 0 0.2rem rgba(233, 30, 99, 0.25);
        }

        .btn-pink {
            background-color: #e91e63;
            color: #fff;
            font-weight: 600;
            font-size: 1.1rem;
            padding: 0.6rem 2rem;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }

        .btn-pink:hover {
            background-color: #d81b60;
        }

        textarea[readonly] {
            background-color: #ffffff;
            color: #2c2c2c;

        }
    </style>
</head>

<body>
    <div class="container">
        <h2>AI Text Rewriter</h2>
        <p class="subtitle">Rewrite any content to match your learning pace</p>

        @if ($errors->any())
            <div class="alert alert-danger">
                {{ $errors->first() }}
            </div>
        @endif

        <form method="POST" action="/rewriter" enctype="multipart/form-data">
            @csrf

            <!-- Input Text (optional instead of PDF) -->
            <div class="mb-4">
                <label for="input_text" class="form-label">Enter Text (optional)</label>
                <textarea class="form-control" id="input_text" name="input_text" rows="6"
                    placeholder="Paste or type text here if you're not uploading a PDF..."></textarea>
            </div>

            <!-- Upload PDF -->
            <div class="mb-4">
                <label for="pdf" class="form-label">Upload PDF</label>
                <input type="file" class="form-control" id="pdf" name="pdf" accept="application/pdf" />
            </div>

            <!-- Learning Speed Selection -->
            <div class="mb-4">
                <label for="learner_type" class="form-label">Learning Pace</label>
                <select class="form-select" id="learner_type" name="learner_type" required>
                    <option value="" disabled selected>Select learning pace</option>
                    <option value="slow">Slow Learner</option>
                    <option value="average">Average Learner</option>
                    <option value="fast">Fast Learner</option>
                </select>
            </div>

            <!-- Submit Button -->
            <div class="mb-4 text-center">
                <button type="submit" class="btn btn-pink">Rewrite</button>
            </div>
        </form>

        <!-- Adaptive Content Output -->
        <div class="mb-4">
            <label for="generate_output" class="form-label">Rewritten Output</label>
            {{-- <textarea class="form-control" id="adaptive_content" name="adaptive_content" rows="10" readonly></textarea> --}}
            <textarea id="generate_output" class="form-control" name="generate_output" rows="10" readonly>{{ $response ?? '' }}</textarea>
        </div>
    </div>
</body>

</html>
