11




kubeadm init \
--apiserver-advertise-address=192.168.43.143 \
--image-repository registry.aliyuncs.com/google_containers \
--kubernetes-version v1.23.6 \
--service-cidr=10.96.0.0/12 \
--pod-network-cidr=10.244.0.0/16 \
--ignore-preflight-errors=all


- name: Stop Kubelet Service
  command: systemctl stop kubelet
  when: ansible_os_family == 'RedHat'

- name: Upgrade Containerd
  yum:
    name: containerd.io={{ containerd_version }}
    state: latest
  when: ansible_os_family == 'RedHat'

- name: Start Containerd
  command: systemctl start containerd
  when: ansible_os_family == 'RedHat'

- name: Restart Kubelet Service
  command: systemctl restart kubelet
  when: ansible_os_family == 'RedHat'