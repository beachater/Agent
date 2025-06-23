<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CK AI Tools</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"
    integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
  <style>
  body {
    font-family: 'Poppins', sans-serif;
    background-color: #f4f7fb;
    color: #333;
    padding-top: 60px;
  }

  .hero {
    background-color: #fff;
    padding: 50px 20px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
    text-align: center;
    border-radius: 12px;
    margin-bottom: 40px;
  }

  .hero h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #EC298B;
  }

  .section-title {
    margin-top: 30px;
    margin-bottom: 20px;
    font-weight: 600;
    font-size: 1.75rem;
    color: #EC298B;
    text-align: center;
  }

  .tool-item {
    background-color: #ffffff;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    transition: transform 0.2s;
    
  }

  .tool-item:hover {
    transform: translateY(-3px);
  }

  .tool-item h5 {
  font-weight: 600;
  margin: 8px;
  color: #000;
  transition: color 0.2s ease;
  padding:10px;
}

.tool-item h5:hover {
  color: #EC298B;
}

.tool-item a {
  color: #000 !important;
  text-decoration: none;
  font-weight: inherit; /* <- Keeps it as bold as the h5 */
}

.tool-item a:hover {
  /* text-decoration: underline; */
  color: #EC298B !important;
}


  .footer {
    margin-top: 60px;
    padding: 20px 5px 20px 5px;
    background-color: #e9ecef;
    text-align: center;
    font-size: 0.9rem;
    color: #555;
  }
  
</style>

</head>

<body>

  <div class="container">
    <div class="hero">
      <h1>Welcome to CK Children's Publishing AI Tools</h1>
      <p class="lead mt-3">CK Children’s Publishing’s suite of AI-powered tools is designed to support students in
        developing strong reading and writing skills. Whether you're working on an assignment, exploring a new
        topic, or refining your writing, our tools are here to help.</p>
    </div>

    <div class="section-title">Available Tools</div>
    <div class="row gx-4">
  <div class="col-md-6">
    <div class="tool-item">
      <h5>🔤<a href="http://192.168.50.144:8000/leveler" target="_blank">Text Leveler</h5>
      <p>Adjust the reading difficulty of any text to match your comfort and comprehension level.</p>
    </div>
  </div>
  <div class="col-md-6">
    <div class="tool-item">
      <h5>🧠<a href="http://192.168.50.238:8000/" target="_blank">Text Summarizer</a></h5>
      <p>Generate clear, concise summaries of longer texts to improve understanding and retention.</p>
    </div>
  </div>
</div>

<div class="row gx-4">
  <div class="col-md-6">
    <div class="tool-item">
      <h5>✍️ <a href="http://192.168.50.127:8000/tutor" target="_blank">Conceptual Understanding</a></h5>
      <p>Receive thoughtful suggestions on grammar, structure, and clarity to improve your writing.</p>
    </div>
  </div>
  <div class="col-md-6">
    <div class="tool-item">
      <h5>♻️ <a href="http://192.168.50.123:8000/rewriter" target="_blank"> Text Rewriter</h5>
      <p>Rephrase sentences and paragraphs while maintaining original meaning — useful for revision and learning new ways to express ideas.</p>
    </div>
  </div>
</div>

<div class="row gx-4">
  <div class="col-md-6">
    <div class="tool-item">
      <h5>😎 <a href="http://192.168.50.18:5001/proofreader" target="_blank">Text Proofreader</a></h5>
      <p>Adjust the reading difficulty of any text to match your comfort and comprehension level.</p>
    </div>
  </div>
</div>

 <div class="section-title">Why Use CK AI Tools?</div>
        <ul class="list-group list-group-flush mb-4">
            <li class="list-group-item">Designed specifically for student readers and writers</li>
            <li class="list-group-item">Easy to use, with instant, reliable results</li>
            <li class="list-group-item">Supports independent learning and classroom engagement</li>
            <li class="list-group-item">Backed by CK Children’s Publishing's commitment to educational excellence</li>
        </ul>

        <div class="text-center mb-5">
            <p class="fw-bold">Begin your journey toward stronger literacy today.</p>
        </div>
    </div>

    <div class="footer">
        &copy; {{ date('Y') }} CK Children’s Publishing. All rights reserved.
    </div>

</body>

</html>