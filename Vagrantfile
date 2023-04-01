Vagrant.configure("2") do |config|
  config.vm.box = "michael-slx/arch64-develop"

  config.vm.hostname = "vm-weewx-wll-test"
  config.vm.network "public_network"

  config.vm.provider "virtualbox" do |v|
    v.memory = 8192
    v.cpus = 8
  end

  config.vm.provision :shell, path: "vm/provision.sh", privileged: false, keep_color: true
end
