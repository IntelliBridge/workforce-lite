# ib-fiore-icd-chatbot

### Launching docker compose

```
    docker compose build open-webui # Build main container
    docker compose up # Can use -d for detached head
    # in other terminal
    curl -o ollama/Mistral-7B-Instruct-v0.3-Q2_K.gguf https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q2_K.gguf
    docker cp ollama/Mistral-7B-Instruct-v0.3.Q2_K.gguf ollama:/tmp/
    docker cp ollama/Modelfile ollama:/tmp/
    # Create shell inside container
    docker exec -it ollama bash
    cd /tmp
    # create model from modelfile
    ollama create dylans-model -f Modelfile
```

## From UI

Once on the UI you can create a knowledgebase from "Workspace>Knowledge> '+' ".

In order to tag a knowledge base when asking a question, use the \#\<collection name\>. 


### Cloning the Repository with Submodules
When cloning the repository for the first time, use the --recurse-submodules flag to clone the submodule along with the main repository:


    git clone --recurse-submodules <url-of-your-repo>
For example:


    git clone --recurse-submodules https://github.com/yourusername/your-repo.git
This command will clone both the main repository and the submodule at the same time.

### Pulling Latest Changes from the Main Repository and Submodule
If you already have the repository cloned but need to pull the latest changes (including updates to the submodule), follow these steps:

Pull changes for the main repository:

    git pull origin main
After pulling changes for the main repository, update the submodule by running:

    git submodule update --recursive --remote
This will fetch the latest changes from the submodule repository and update your local submodule directory.

### Committing Changes to the Submodule
If you've made changes within the submodule directory and want to commit those changes, follow these steps:

Navigate to the submodule directory:

    cd submodules/forked-repo
Stage and commit changes within the submodule: Stage and commit changes just like you would in any Git repository:

    git add .
    git commit -m "Your commit message for the submodule"

Push changes to the submodule's repository: 
If you want to push your changes back to the submodule's repository (especially if it’s your fork), you can do so by pushing to the submodule's remote repository:


    git push origin <branch-name>
Go back to the main repository:  Once you’ve committed and pushed your changes to the submodule, go back to the main repository:


    cd ../..
Stage and commit the submodule update in the main repository: The main repository now points to a new commit in the submodule. Stage and commit this change to your main repository:

    git add submodules/forked-repo
    git commit -m "Update submodule to latest commit"
Push the changes to the main repository: Finally, push the changes to your main repository:

    git push origin main
