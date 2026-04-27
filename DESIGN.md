# FlickIndex - Group Design Document

**Team Members:** Ahmadshah, Marian, Michael, Lewis
**Date:** 27th April 2026
**Version:** 1.1

## 1. Project Overview

We are building a movie recommendation application that helps the user discover movies they are likely to enjoy based on their preferences and viewing history. This is for the people who have the problem of spending more time looking for a movie to watch than actually watching a movie that is what this application will achieve to solve.

## 2. Goals & Objectives

* **Core Goal:** User can search for movies by title, actor, and genre to recieve see accurate results.
* **Secondary Goals:** User can add and remove from a list of favourites, a watchlist, recently viewed.

## 3. The User Journey

* **The Experience:** User uses a simple text search to find the movie
* **Inputs:** Uses keyboard for searches and mouse for selecting

## 4. Program Logic (Step-by-Step)

1. **Initialization:** We will start by importing any needed modules and set up global variables that are to be used by the terminal only.
2. **Input Phase:** We will prompt the user to enter their preferred genres to watch and movies they have already watched
3. **Processing Phase:** We will process the user's answers and compare it to the database of movies. We will write a program that filters movies already watched and choose movies that match their interest
4. **Output Phase:** We will display a personalised list of recommended movies
5. **Loop/Cleanup:** We will ask the user if they want more recommendations/ update their preferences/ exit the application

## 5. Team Responsibility Breakdown

* **Ahmadshah:** [Lead on Data Storage and File I/O.]
* **Marian:** [Lead on Documentation & Testing]
* **Michael:** [Lead on app.py (frontend) logic.]
* **Lewis:** [Lead on main.py (backend) logic.]

## 6. Module & Function Breakdown

* **`main.py`**: The file that deals with the TMDB API and backend logic. (Handled by: [Lewis])
* **`app.py`**: The file that deals with the Textual UI and frontend logic. (Handled by: [Michael])
* **`storage_module.py`**: Functions for reading/writing storage files. (Handled by: [Ahmadshah])

## 7. Data Storage & Structures
* **Variables/Collections:** We will store movie collections in lists and we will store more detailed information in dictionaries such as genre, rating, release year. Viewing history will be stored in a list, so the program can avoid giving the same movies. User preferences will be stored in dictionaries so that reommendations can be personalised in detail
* **Persistence:** We store data in an external JSON file

## 8. Development Timeline (Milestones)
1. **Milestone 1:** [11.3] - We will have the basic project structure and main menu working.
2. **Milestone 2:** [25.3] - We will have our individual modules connected and talking to each other.
3. **Milestone 3:** [29.4] - We will finish testing for bugs and submit the final version.

### Team Checklist:
* **Consistency:** Using snake_case and keeping the GitHub repository updated.
* **Communication:** Any communication should be done via Teams or Whatsapp.
* **Integration:** Regular merges and pulls from the main branch to keep up to date.