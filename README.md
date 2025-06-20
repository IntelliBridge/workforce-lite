# ib-fiore-icd-chatbot

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit to Agile Defense and third party creators
- NonCommercial — You may not use the material for commercial purposes in any form
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license

[![CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)


### Launching stack via docker compose

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

## Building new open-webui container

After making code changing to the submodule you can rebuild the image for local testing by:
    docker compose build open-webui
    
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

### Running helm chart

There are two helm charts you can chose from: helm/ (basic using commercial images) and ironbank/ (using ironbank images). If you would like to run the ironbank helm chart you must first create a secrets registry:

    kubectl create secret docker-registry regcred \
      --docker-server=registry1.dso.mil \
      --docker-username=your-username \
      --docker-password=your-password \
      --docker-email=your-email

To run the helm chart simply:
    helm install <name> ./chart

In order to see the appplication you will need to forward the frontend pod:

    minikube service open-webui --url

You can also view the minikube dashboard with:

    minikube dashboard

But you may need to install add-ons first:

    minikube addons enable metrics-server
    minikube addons enable ingress
    minikube addons enable dashboard

In order to activate the model into the application:

    kubectl get pods # Use this to find the ollama pod name
    kubectl cp /path/to/model.gguf <ollama-pod>:/tmp/
    kubectl cp /path/to/Modelfile <ollama-pod>:/tmp/
    kubectl exec -it <ollama-pod> -- bash
    cd /tmp
    ollama create dylans-model -f Modelfile


### Deploying new code

Debian

    install python 3.11 
    install nvm 
    install node (version 22) (nvm use 22)
    get your registry1 crednetials
     - log in to platform 1 using SSO, you may need to create an account (https://p1.dso.mil/)
     - go to harbor: https://registry1.dso.mil/harbor/projects
     - Get username and CLI token from top right 
    login to registry1
     - docker login -u <username> -p <cli-secret> registry1.dso.mil
    build wheel (see instructions below)
    build open-webui image (see instruction below)
    build opensearch image (see instrctions below)
    edit docker compose if needed
     - If you are using different image names this should be reflected in compose file
     - If you are using GPUs be sure and ammend dockerfile or use gpu enable docker-compose file


#### GPU resources 


In order to run on GPU hardware one must have all of the nvidia drivers working
as well as the nvidia runtime for docker: 

    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker

Your docker compose file must be configured to use gpu resources: 

    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    
#### Installing and using nvm

Install nvm and use node 22.

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    nvm install 22
    nvm use 22 

Check and make sure your node and npm versions are satisfactory with what is in the current package.json.
    npm --version
    node --version

Make sure you have python3.11 installed
    brew install python@3.11


#### In order to develop changes 

Make your changes to  the submodule, <it>open-webui</it>.

Build a new wheel from open-webui and use to build the new docker image.

    cd open-webui
    python3.11 -m build --wheel
    cp dist/<wheelfile.whl> ../open-webui-ironbank-container/
    cd ../open-webui-ironbank-container/
    # Make sure the requirements.txt file references the new wheel file
    cat requirements.txt
    docker build -t <imagename>:latest .
    # Push image to image repository
    docker login
    docker tag <latestbuild>:latest <dockerhub-username>/<imagename>:<release version>
    docker push <dockerhub-username>/<imagename>:<release version>

Build a new wheel from opensearch and use to build the new docker image.

    cd opensearch-ironbank-container
    docker build -t <imagename>:latest .
    # Push image to image repository
    docker login
    docker tag <latestbuild>:latest <dockerhub-username>/<imagename>:<release version>
    docker push <dockerhub-username>/<imagename>:<release version>

You can now make sure the image references in the open-webui-deployment.yaml file is pointing to the image in dockerhub and do

    helm install <name> ./<helm_chart>

In order to see the application you will need to forward the frontend from minikube:

    minikube service open-webui --url


# Application Navigation and Usage Notes

### to add pdfs to chatbot 
- From desktop
	- Open browser of choice
	- search `localhost:3000`
	- sign in if asked
	 - Workspace on left bar
	 - Knowledge tab center top of window
	 - create new collection or add to existing
	 - click the + icon to select option
	 - click upload file or folder
	 - navigate and upload file/folder for training

### Access web page 
- make sure docker containers are up
	- `sudo docker ps`
- if not up
	- `cd /home/user/projects/ib-fiore-icd-chatbot`
	- `sudo docker compose -f docker-compose.ironbank.yml up`
- in a browser, search: `localhoast:3000`

### setting up model with .gguf file
- `sudo docker cp <model_name>.gguf <ollama_ID>:/tmp`
- `sudo docker cp Modelfile <ollama_ID>:/tmp`
- `sudo docker exec -u root -it <ollama_ID> bash` to get into vm
	- `cd /tmp/`
	- `ollama create <model_name>`

### Query question to specific knowledge collection
- `#new stuff` to knowledge base name

### to configure the model 
- name in bottom left
- settings
- documents in top right
- embedding model set default-> ollamma
- specify model name below
- set hybrid search to on
- give it the same model name for re-ranking model
- change top k to 6 (double the current)

### current models in use:
- Gemma3:12b
- nomic-embed-text
- Mistral

Models can be found at 'https://huggingface.co/QuantFactory/Mistral-7B-v0.3-GGUF/tree/main'
