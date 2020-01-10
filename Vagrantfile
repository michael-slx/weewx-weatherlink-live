Vagrant.configure("2") do |config|
  config.vm.box = "michael-slx/arch64-base"

  config.vm.network "public_network", auto_config: false

  config.vm.provider "virtualbox" do |v|
    v.memory = 8192
    v.cpus = 8
  end

  config.vm.provision :shell, path: "testing/bin/provision.sh", privileged: false
end
