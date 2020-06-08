import multiprocessing as mp
import os
import sys
import pandas as pd
import numpy as np
import prctl

class chroot:
    def __init__(self, root_dir, do_bindings=True, remove_bindings_dying=True, unchroot_dying=True):
        self.root_dir = root_dir
        self.unchroot_dying = unchroot_dying
        self.do_bindings = do_bindings
        self.remove_bindings_dying = remove_bindings_dying

    def __enter__(self):
        self.real_root = os.open("/", os.O_RDONLY)

        if self.do_bindings:
            folders = { "proc": "proc", "sys": "sysfs", "dev": "" }
        
            for folder in folders.keys():
                full_path = self.root_dir + "/" + folder
                
                if not os.path.exists(full_path):
                    os.mkdir(full_path)

                if folders[folder] == '':
                    os.system("mount --bind -o ro /%s %s" % (folder, full_path))
                else:
                    os.system("mount -t %s -o ro /%s %s" % (folders[folder], folder, full_path))
        os.chroot(self.root_dir)

    def __exit__(self, exc_type, exc_val, traceback):
        os.system("sync")
        if self.unchroot_dying:
            os.fchdir(self.real_root)
            os.chroot('.')
        if self.do_bindings and self.remove_bindings_dying:
            os.system("umount -l %s/dev" % self.root_dir)
            os.system("umount -l %s/proc" % self.root_dir)
            os.system("umount -l %s/sys" % self.root_dir)
        os.close(self.real_root)

def sandboxed(chroot_path, untrusted_code, source, result):

    with chroot(chroot_path, False, False, False):

        prctl.securebits.keep_caps = True
        os.setgroups([1000])
        os.setgid(1000)
        os.setuid(1000)

        mf = source.get()
        try:
            exec(untrusted_code)
        except Exception as ex:
            result.put(mf)
            raise
        result.put(mf)

if __name__ == '__main__':

    mp.set_start_method('spawn')
    chroot_path = '/sandbox'

    df = pd.DataFrame(np.random.randint(0,5000000,size=(5000000, 10)), columns=list('ABCDEFGHIJ'))

    print("Initial dataframe state:")
    print(df)

    untrusted_code = """
mf.A=np.random.randint(0,5000000,size=(5000000, 1))
"""

    df_source_queue = mp.Queue()
    df_result_queue = mp.Queue()
    p = mp.Process(target=sandboxed, args=(chroot_path, untrusted_code, df_source_queue, df_result_queue))
    p.start()
    df_source_queue.put(df)
    print(df_result_queue.get())
    p.join()
