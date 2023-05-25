# Synced directory with the temporary storage server `pioneer.nntb.no`

Here we fetch the raw results from `pioneer.nntb.no`.
Each folder is an expriment instance run and is fetched "as is" from the 
temporary storage server `pioneer.nntb.no`.
It includes the files created by the container as well as as dignostic files
created automatically, such as the deployment log and a log with everything
printed on the screen.


It is a good idea to fetch the results soon after they are created, because
`pioneer.nntb.no` will delete them after a few months.
This directory can be the starting point of a pipeline that further processes
results for exploratory analysis or for the creation of dashboards and reports.