<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Text Proofreader</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container my-5">
        <div class="card shadow-sm">
            <div class="card-body">
                <h1 class="card-title text-center text-primary mb-3">🤖 Welcome to AI Agent Text Proofreader</h1>
                <h5 class="text-muted text-center mb-4">
                    This tool helps you proofread your text using AI—fixing grammar, spelling, punctuation, and clarity.
                </h5>

                <form action="/register" method="POST">
                    @csrf
                    <div class="mb-3">
                        <label for="profile_type" class="form-label fw-semibold">Choose a profile type:</label>
                        <select class="form-select" id="profile_type" name="profile_type">
                            <option value="academic">Academic</option>
                            <option value="casual">Casual</option>
                            <option value="concise">Concise</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="text" class="form-label fw-semibold">Enter your text:</label>
                        <textarea class="form-control" id="text" name="text" rows="10" placeholder="Paste your text here..."></textarea>
                    </div>

                    <div class="d-grid d-md-flex justify-content-md-end">
                        <button type="submit" class="btn btn-primary px-4">Submit</button>
                    </div>
                </form>
            </div>
        </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
