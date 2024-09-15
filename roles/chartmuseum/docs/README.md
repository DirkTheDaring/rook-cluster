Use the helm push plugin
# 1
helm plugin install https://github.com/chartmuseum/helm-push
# 2
helm repo add chartmuseum https://chartmuseum.<YOURDOMAIN>/<YOURPROJECTNAME>
  Example: 
  helm repo add https://chartmuseum.example.com/myproject

# 3 
helm cm-push 


