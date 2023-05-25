# Example NorNet / MONROE experiment repository
This is an example repository with all the scripts needed to manage the whole
lifecycle of an experiment on the NorNet / MONROE platform.

We will create a simple experiment (i.e. ping `www.google.com` 10 times), run it
on the platform and finally retrieve the results.

## The lifecycle of an experiment in brief

The steps we have to follow from experiment definition to having results are:

1. We first "pack" our scripts into a container.
2. If needed we prepare some server side scirpts. This is needed if, for
example, our experiment follows the client-server paradigm.
3. We use some helper scripts to interface with the scheduler and define on
which nodes and when the container will be deployed and run.
Alternativly we can use the web interface of the scheduler at
`https://haugerud.nntb.no`.
4. We retrieve the results from the temporary storage server `pioneer.nntb.no`.

## Repository structure

* **simpleping**: The directory of the container.
We must always use the name of the container as the name of is directory,
because the scripts use the directory  name to name to tag and push the
container to dockerhub.
Here the container is called `simpleping`, so we also name the directory
`simpleping`.
Do not use capital letters.
* **scheduling**: Documentation and scripts on how to interact with the
scheduler.
The `README.md` files explains how to use the API.
There are also some helper scripts to interact with the scheduler
programmatically.
* **nodeDevelopment**: instructions on how to connect directly on a node to 
test your containers.
* **nodeResults**: Directory where we fetch the files created by the
experiements.
It includes the files created by the container as well as as dignostic files
created automatically, such as the deployment log and a log with everything
printed on the screen.
Each folder is an expriment instance run and is fetched "as is" from the 
temporary storage server `pioneer.nntb.no`.
