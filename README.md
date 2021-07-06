# News Pulse

News Pulse is an interactive dashboard that summarizes publishing activity by The Guardian over a user specified period of time. A user can input a range of time and explore overall publishing volume, different keywords, and topics created from a Non-Negative Matrix Factorization NLP algorithm.

This project is a full end-to-end data pipeline, NLP machine learning algorithm, and front end web application demonstrating my ability to engineer an efficient system to acquire, store, model, and visualize data. Below is a high level visual representation of the pipeline.

![pipeline](https://github.com/mattrimol/news_pulse/blob/main/images/pipeline.png)

## Repo Directory:

#### Code:

- Data Acquisition & Storage
  - [Update Database with New Content](https://github.com/mattrimol/news_pulse/blob/main/app/update_content.py)
  - [Functions for API & Pipeline](https://github.com/mattrimol/news_pulse/blob/main/app/guardian_data_pipeline.py)
- Machine Learning NLP Model
  - [Fit a Model to Random Sample of Data](https://github.com/mattrimol/news_pulse/blob/main/app/fitting.py)
  - [Functions for NLP Model](https://github.com/mattrimol/news_pulse/blob/main/app/news_nlp.py)
- Front End Web Application
  - [Code to Run Streamlit App](https://github.com/mattrimol/news_pulse/blob/main/app/news_cycle.py)
  - [Streamlit Functions](https://github.com/mattrimol/news_pulse/blob/main/app/streamlit_library.py)

### Presentation:

- [Video Presentation](https://github.com/mattrimol/news_pulse/blob/main/presentation/news_pulse_presentation.mp4)
- [Slides](https://github.com/mattrimol/news_pulse/blob/main/presentation/news_pulse_slides.pdf)

