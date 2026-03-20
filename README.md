#  Serverless Facial Recognition Pipeline on AWS

![AWS](https://img.shields.io/badge/AWS-Lambda-orange)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![ML](https://img.shields.io/badge/MachineLearning-FaceRecognition-green)
![Architecture](https://img.shields.io/badge/Architecture-Serverless-purple)

A **scalable serverless video analysis system** that performs **automatic facial recognition on uploaded videos** using AWS cloud services and deep learning models.

This project demonstrates **cloud-native architecture, serverless computing, distributed processing, and machine learning integration**.

The system uses an **event-driven architecture built with AWS Lambda, Amazon S3, Docker, OpenCV, and PyTorch** to process video uploads, detect faces, and identify individuals automatically.

---

#  Key Features

* Serverless **event-driven architecture**
* **Automatic video processing pipeline**
* **Deep learning face recognition**
* **Docker-based Lambda deployment**
* Scalable processing using **AWS Lambda concurrency**
* Handles **100 video requests under 300 seconds**

---

#  Architecture Overview

The application is implemented as a **multi-stage serverless pipeline**.

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/94d0a87a-2e57-4286-8caa-bda80ea57267" />


### AWS Services Used

| Service          | Purpose                                             |
| ---------------- | --------------------------------------------------- |
| **Amazon S3**    | Storage for videos, frames, and recognition results |
| **AWS Lambda**   | Serverless compute for processing pipeline          |
| **Docker (ECR)** | Packaging ML dependencies                           |
| **CloudWatch**   | Logging and monitoring                              |

This architecture allows the system to **scale automatically with incoming workloads without managing infrastructure**.

---

#  Pipeline Workflow

###  Video Upload

Users upload `.mp4` videos to the **Input S3 Bucket**.

```
<ASU_ID>-input
```

Each upload automatically triggers the **Video Splitting Lambda function**.

---

###  Video Splitting Lambda

Responsibilities:

* Download video from S3
* Extract a frame using **FFmpeg**
* Store the extracted frame in the Stage-1 bucket

Example FFmpeg command:

```bash
ffmpeg -i input_video.mp4 -vframes 1 output.jpg
```

Output example:

```
test_01.mp4 → test_01.jpg
```

---

###  Face Recognition Lambda (Docker)

The second Lambda is deployed using **Docker containers** to package machine learning dependencies.

Responsibilities:

1. Download frame image from S3
2. Detect faces using **MTCNN**
3. Generate embeddings using **InceptionResnetV1**
4. Compare embeddings with stored dataset
5. Identify the closest match
6. Write results to output bucket

Example:

```
test_01.jpg → test_01.txt
```

---

#  Machine Learning Pipeline

### Face Detection

Faces are detected using **MTCNN (Multi-task Cascaded CNN)**.

```python
mtcnn = MTCNN(image_size=240)
```

---

### Face Embedding Generation

Feature vectors are generated using a pretrained model:

```
InceptionResnetV1 (pretrained on VGGFace2)
```

---

### Identity Matching

Embeddings are compared with stored embeddings using Euclidean distance:

```python
distance = torch.dist(embedding, stored_embedding)
```

The smallest distance determines the predicted identity.

---

#  S3 Storage Layout

| Bucket             | Purpose                    |
| ------------------ | -------------------------- |
| `<ASU_ID>-input`   | Stores uploaded videos     |
| `<ASU_ID>-stage-1` | Stores extracted frames    |
| `<ASU_ID>-output`  | Stores recognition results |

Example flow:

```
Input bucket
   test_01.mp4

Stage-1 bucket
   test_01.jpg

Output bucket
   test_01.txt
```

---

#  Repository Structure

```
facial-recognition-aws/
│
├── lambda_function.py
│   Video splitting Lambda implementation
│
├── fac_recog.py
│   Face recognition pipeline
│
├── Dockerfile
│   Container image for ML dependencies
│
├── requirements.txt
│
└── README.md
```

---

#  Docker Deployment

The **face recognition Lambda** is deployed using Docker to package heavy ML libraries.

Dependencies included:

* PyTorch
* facenet-pytorch
* OpenCV
* Torchvision
* NumPy
* Pillow

Example base image:

```
python:3.9-slim
```

Using Docker avoids Lambda size limitations and ensures **consistent runtime environments**.

---

#  System Design

The system follows a **serverless event-driven architecture** optimized for scalability and reliability.

### Event-Driven Processing

S3 triggers Lambda functions automatically whenever a new video is uploaded.

This enables **real-time processing without polling systems**.

---

### Stateless Pipeline

Each Lambda function is **stateless** and communicates via S3.

Benefits:

* horizontal scalability
* improved fault tolerance
* simplified architecture

---

### Containerized ML Inference

The face recognition model requires large dependencies such as PyTorch.

Using **Docker containers for Lambda** ensures:

* dependency consistency
* easier deployment
* no Lambda package size limitations

---

#  Scalability

The architecture supports **massively parallel processing**.

Each uploaded video triggers an independent Lambda execution.

Example:

```
100 videos uploaded
→ 100 Lambda executions
→ processed in parallel
```

AWS automatically scales Lambda instances based on demand.

---

#  Performance

The system was tested using an automated **100-video workload generator**.

### Results

| Metric                | Result            |
| --------------------- | ----------------- |
| Total requests        | 100               |
| End-to-end latency    | **< 300 seconds** |
| Frames generated      | 100               |
| Recognition outputs   | 100               |
| Pipeline success rate | 100%              |

The system successfully met all project performance objectives.

---


# ⭐ Future Improvements

* GPU-based inference
* REST API using API Gateway
* Web dashboard for visualization
* Real-time security alerting system using SES/SNS

---

# 👨‍💻 Author

**Shreyansh Raj**

Software Engineer | AWS Cloud Developer
M.S. Computer Science — Arizona State University

GitHub
https://github.com/shreyanshraj
