from promptflow.client import PFClient

# Please protect the entry point by using `if __name__ == '__main__':`,
# otherwise it would cause unintended side effect when promptflow spawn worker processes.
# Ref: https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
  # PFClient can help manage your runs and connections.
  pf = PFClient()

  # Set flow path and run input data
  flow = "./web-classification" # set the flow directory
  data= "./web-classification/data.jsonl" # set the data file

  # create a run, stream it until it's finished
  base_run = pf.run(
      name="myrun",
      flow=flow,
      data=data,
      stream=True,
      # map the url field from the data to the url input of the flow
      column_mapping={"url": "${data.url}"},
  )

  # get the inputs/outputs details of a finished run.
  details = pf.get_details(base_run)
  details.head(10)
  # visualize the run in a web browser
  pf.visualize(base_run)