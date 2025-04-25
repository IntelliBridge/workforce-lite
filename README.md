# ib-fiore-icd-chatbot

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

Install nvm and use node 22.

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    nvm install 22
    nvm use 22 

Check and make sure your node and npm versions are satisfactory with what is in the current package.json.
    npm --version
    node --version

Make sure you have python3.11 installed
    brew install python@3.11

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
    python3.11 -m build --wheel
    cp dist/<wheelfile.whl> ../opensearch-ironbank-container/
    cd ../opensearch-ironbank-container/
    # Make sure the requirements.txt file references the new wheel file
    cat requirements.txt
    docker build -t <imagename>:latest .
    # Push image to image repository
    docker login
    docker tag <latestbuild>:latest <dockerhub-username>/<imagename>:<release version>
    docker push <dockerhub-username>/<imagename>:<release version>

You can now make sure the image references in the open-webui-deployment.yaml file is pointing to the image in dockerhub and do

    helm install <name> ./<helm_chart>


In order to see the application you will need to forward the frontend from minikube:

    minikube service open-webui --url



