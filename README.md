![Jukebox](Dscn2823-Wurlitzer-3500-Zodiac-On.jpg](Dscn2823-Wurlitzer-3500-Zodiac-On.jpg)

# random_music

Problem to solve: I have a collection of YouTube bookmarks not in a playlist on any application.  I want to be surprised by a randomized music selection, selected from my bookmarks.

**Note**: In this repo, I tested both pre-commit for git and GitHub actions using Yaml and confirmed both executed flake8 for linting.  I like both, but Actions is more foolproof.
## Future plans

- [x] See issues in GitHub
 
## Important disclaimer

THIS CODE IS STILL TERRIBLE.  
Was: *I wrote it a long time ago and just now got around to adding it to a repo.  It was throwaway, and I'm now setting a goal to make it not throwaway.*

Now: **One thing I like to do is take ancient, horrible code of mine and refactor it-- use it as a playground for improvements**

I am testing out ideas about coding practices here as I clean up some truly awful rushed coding.

Not everything has to be a glamorous project to demonstrate the power of refactoring :)

**Look at the start of process here**
What I do at work is a lot more complex, but I was very quickly able to assemble:
* a primitive CI/CD process with 
    * Git Hooks instantiated through pre-commit
    * GitHub Actions
* Issue templates for 
    * Bugs
    * Features
    * Information requests

I'll continue work on the process here, even if the code languishes a bit.

## Getting Started

Clone the repository to your local machine, ensure you have your bookmarks or playlist file available, and configure the required paths in a `config.json` file.

```bash
git clone https://github.com/ErikPohl444/random_music.git
cd random_music
```

## Prerequisites

- Python 3.8 or higher
- Google Chrome (the path to the Chrome executable must be specified in `config.json`)
- An exported Chrome bookmarks file or a CSV/Excel file containing your song names and YouTube URLs

Install the required Python packages using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Installing

1. Clone this repository.
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `config_template.json` to `config.json` and update it with the correct paths for your Chrome executable and bookmarks or playlist file.
4. Place your bookmarks or playlist file in the project directory or update the path in `config.json` accordingly.

## Running the Tests

This assumes you've already installed the code and the requirements in requirements.txt.

To run the tests for this project, follow these steps:

  Run all tests in the `/tests` folder using pytest:

   ```bash
   pytest tests/
   ```

   Or, to run a specific test file:

   ```bash
   pytest tests/test_main.py
   ```
   
## Contributing

For now, I'd be excited to receive pull requests.  I don't have rules for contributing right now.

## Authors

* **Erik Pohl** - *Initial work* - 

Also see the list of GitHub contributors.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to everyone who has motivated me to learn more.
