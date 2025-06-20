@extends('layouts.app')

@section('content')
<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-md-8">
      <div class="card shadow">
        <div class="card-body">
          <h2 class="card-title text-center mb-4">AI Tutor Assistant</h2>

          <form action="{{ url('/tutor') }}" method="POST" enctype="multipart/form-data">
            @csrf

            <div class="mb-3">
              <label class="form-label">Grade Level</label>
              <input type="text" class="form-control" name="grade_level" required>
            </div>

            <div class="mb-3">
              <label class="form-label">Input Type</label>
              <select class="form-select" name="input_type" id="input_type">
                <option value="topic">Topic</option>
                <option value="pdf">PDF</option>
              </select>
            </div>

            <div class="mb-3" id="topic-input">
              <label class="form-label">Topic</label>
              <input type="text" class="form-control" name="topic">
            </div>

            <div class="mb-3 d-none" id="pdf-input">
              <label class="form-label">Upload PDF</label>
              <input type="file" class="form-control" name="pdf_file" accept="application/pdf">
            </div>

            <div class="mb-3">
              <label class="form-label">Additional Context</label>
              <textarea class="form-control" name="add_cont"></textarea>
            </div>

            <button type="submit" class="btn btn-primary">Submit</button>
          </form>

          @if(isset($response))
            <hr class="my-4">
            <h5>AI Tutor Response:</h5>
            <pre class="bg-white border p-3">{{ $response }}</pre>
          @endif

          @error('error')
            <div class="alert alert-danger mt-3">{{ $message }}</div>
          @enderror
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  document.getElementById('input_type').addEventListener('change', function () {
    const type = this.value;
    document.getElementById('topic-input').classList.toggle('d-none', type === 'pdf');
    document.getElementById('pdf-input').classList.toggle('d-none', type === 'topic');
  });
</script>
@endsection
