@extends('layouts.app')

@section('content')
<style>
  body {
    background-color: #f4f7fb;
    font-family: 'Poppins', sans-serif;
  }

  .ck-card {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
    padding: 40px;
    border: 1px solid #e4e8f0;
  }

  .ck-btn {
    background-color: #EC298B;
    color: #fff;
    border: none;
    padding: 12px 28px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 16px;
    transition: background-color 0.3s ease;
  }

  .ck-btn:hover {
    background-color: #d32078;
  }

  .ck-title {
    font-size: 2rem;
    font-weight: 600;
    color: #EC298B;
    margin-bottom: 30px;
  }

  label {
    font-weight: 500;
    color: #2c3e50;
  }

  pre {
    white-space: pre-wrap;
    background-color: #f0f4f8;
    border-radius: 8px;
    padding: 15px;
    border: 1px solid #dce3ed;
    font-family: 'Courier New', monospace;
  }

  .form-control,
  .form-select {
    border-radius: 6px;
    border: 1px solid #ccd6e0;
    box-shadow: none;
  }

  .form-control:focus,
  .form-select:focus {
    border-color: #EC298B;
    box-shadow: 0 0 0 0.2rem rgba(236, 41, 139, 0.2);
  }
</style>

<div class="container py-5">
  <div class="row justify-content-center">
    <div class="col-lg-8">
      <div class="ck-card">
        <h2 class="ck-title text-center">AI Tutor Assistant</h2>

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
            <textarea class="form-control" name="add_cont" rows="3"></textarea>
          </div>

          <div class="text-center mt-4">
            <button type="submit" class="ck-btn">Submit</button>
          </div>
        </form>

        @if(isset($response))
          <hr class="my-4">
          <h5 class="fw-bold" style="color:#EC298B;">AI Tutor Response:</h5>
          <pre>{{ $response }}</pre>
        @endif

        @error('error')
          <div class="alert alert-danger mt-3">{{ $message }}</div>
        @enderror
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
