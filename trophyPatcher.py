import Tkinter
import tkFileDialog
import tkMessageBox
import shutil
import sys
import os
import zipfile
import binascii


os.chdir(os.path.dirname(os.path.realpath(__file__)))
def zip(src, dst): #Stolen from PSVIMGTOOLS-FRONTEND (which probably stole it from StackOverflow)
    zf = zipfile.ZipFile("%s" % (dst), "w", zipfile.ZIP_DEFLATED,allowZip64 = True)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'Writing %s To VPK' % (os.path.join(dirname, filename))
            zf.write(absname, arcname)
            print 'Removing '+os.path.join(dirname, filename)
            os.remove(os.path.join(dirname, filename))
    zf.close()

window = Tkinter.Tk()
window.wm_withdraw()
tkMessageBox.showinfo(title="NPWR FOLDER",message="Please select the incompadible game's NPWR Folder\n(trophy/data/NPWRXXXX)")
trophyFolder = tkFileDialog.askdirectory(title="Trophy Folder")
if not os.path.exists(trophyFolder+"/TRPTRANS.DAT"):
    tkMessageBox.showerror(title="NPWR FOLDER", message="Wrong Folder! its located at\nur0:user/00/trophy/data\nand contains the files\n'TRPTRANS.DAT' and 'TRPTITLE.DAT'")
    os._exit(0)
tkMessageBox.showinfo(title=".TRP",message="Please select the incompadbile games DECRYPTED .TRP file\n(use vitashell, or mai/vitamin.)\n(sce_sys/trophy/TROPHY.TRP)")
trophyTRP = tkFileDialog.askopenfilename(title="TRP File",filetypes=[('Trophy Data Files', '*.TRP')])

if not open(trophyTRP,"rb").read().startswith("\xDC\xA2\x4D"): #idiot protection
    tkMessageBox.showerror(title=".TRP",message="This TRP File Is Invalid.. (encrypted?)")
    os._exit(0)

tkMessageBox.showinfo(title=".VPK",message="Please select where you would like the patched game's (.vpk) to be saved.")
trophyVPK = tkFileDialog.asksaveasfilename(title="VPK File",filetypes=[('Vita Package', '*.vpk')])

if trophyVPK.endswith("\\") or trophyVPK.endswith("/"):
    trophyVPK = trophyVPK[:-1]

if not trophyVPK.upper().endswith(".VPK"):
    trophyVPK = trophyVPK + ".vpk"

    
    
if sys.platform.__contains__("win"):
    os.system('psvpfsparser.exe --title_id_src="'+trophyFolder+'" --title_id_dst="'+trophyFolder+'_decrypted" --f00d_url=cma.henkaku.xyz')
else:
    os.system('./psvpfsparser --title_id_src="'+trophyFolder+'" --title_id_dst="'+trophyFolder+'_decrypted" --f00d_url=cma.henkaku.xyz')

trpData = open(trophyFolder+"_decrypted/TRPTRANS.DAT","rb").read()
npCommSign = trpData[400:560]
npCommId = trpData[0x170:0x170 + 0x0C]

gameNpCommSign = binascii.unhexlify("b9dde13b01000000000000003cc3f8965e6643e6c9dcfa5615cadd856f6d064ba62ec13ff0fc79cd6b7d02c230939eb7fec017e84d43c47567ad592d27907cdf2b37c2a8b71ecc616465988113b7a6e6b8ea16bdd08af63cc27c449a91821f8a6a27e597db162cc5fd9b4052ae8f6de6b5341814da2d9004fc4ea4174bfbc0fa3f433d1c6126197389c07ac407988e9cde77edcc3e61c5cc04799602573459fc")
gameNpCommId = "NPWR07688"

shutil.copytree(os.path.dirname(os.path.realpath(__file__))+'/toMod',trophyVPK+"_temp")

gameEboot = open(os.path.dirname(os.path.realpath(__file__))+'/toMod/eboot.bin',"rb").read()
gameEboot = gameEboot.replace(gameNpCommId,npCommId[:-3])
gameEboot = gameEboot.replace(gameNpCommSign,npCommSign)

os.makedirs(trophyVPK+"_temp/sce_sys/trophy/"+npCommId)
open(trophyVPK+"_temp/eboot.bin","wb").write(gameEboot)
shutil.copy(trophyTRP,trophyVPK+"_temp/sce_sys/trophy/"+npCommId+"/TROPHY.TRP")

zip(trophyVPK+"_temp",trophyVPK)
shutil.rmtree(trophyVPK+"_temp")
shutil.rmtree(trophyFolder+"_decrypted")

tkMessageBox.showinfo(title="Done!",message="Done! Patched game created.")
window.destroy()