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
trophyFolder = tkFileDialog.askdirectory(title="Trophy Folder (Press cancel for eboot.bin)")
if trophyFolder == '':
    tkMessageBox.showinfo(title="Eboot.bin?",message="You didnt select a folder!\nwell you can also use eboot.bin to patch the game.\nhowever this might not allways work!\nPlease make sure the eboot.bin is from a maidump or vitamin backup.")
    trophySelf = tkFileDialog.askopenfilename(title="Vita Executable", filetypes=[('Vita Executables', ('*.bin','*.self','*.suprx','*.skprx','*.elf'))])
    if trophySelf == '':
        tkMessageBox.showerror(title="Eboot.bin",message="You didnt select anything!")
        os._exit(0)
elif not os.path.exists(trophyFolder+"/TRPTRANS.DAT"):
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

    

if trophyFolder != '':
    if sys.platform.__contains__("win"):
        os.system('psvpfsparser.exe --title_id_src="'+trophyFolder+'" --title_id_dst="'+trophyFolder+'_decrypted" --f00d_url=cma.henkaku.xyz')
    else:
        os.system('./psvpfsparser --title_id_src="'+trophyFolder+'" --title_id_dst="'+trophyFolder+'_decrypted" --f00d_url=cma.henkaku.xyz')

    trpData = open(trophyFolder+"_decrypted/TRPTRANS.DAT","rb").read()
    npCommSign = trpData[400:560]
    npCommId = trpData[0x170:0x170 + 9]
    print binascii.hexlify(npCommSign)
elif trophySelf != '':
    trpData = open(trophySelf,"rb").read()
    try:
        i = trpData.index("\xb9\xdd\xe1\x3b")
        npCommSign = trpData[i:i + 0xA0]
        try:
            i = trpData.index("NPWR")
        except:
            i = trpData.index("NPXS") # NPTrophy Sample Code uses NPXS..
        npCommId = trpData[i:i+9]

        print binascii.hexlify(npCommSign)
    except:
        tkMessageBox.showerror(title="Eboot.bin", message="NpCommSign or NpCommId was not found in the eboot")
        os._exit(0)
gameNpCommSign = binascii.unhexlify("b9dde13b01000000000000001efa85f5b119c4750aa408e9d8b86f833a0bb0a11f0fda592926ca8c5ef715638930dce4b53c710eddb5b92f7c0cecc6e861d1da194f7724fbdbc7856b9d429065bde7f1dc2c7b9b36296e046260caa495945ead22d9f10be6410c02312390b51a013c8924ec4827c4b3f97d5e74f6be1cb86257e1f4263a8d85a20a80937f773d4146b2f24224c9f9ee53406aaf5881043e7099")
gameNpCommId = "NPXS00032"

shutil.copytree(os.path.dirname(os.path.realpath(__file__))+'/toMod',trophyVPK+"_temp")

gameEboot = open(os.path.dirname(os.path.realpath(__file__))+'/toMod/eboot.bin',"rb").read()
gameEboot = gameEboot.replace(gameNpCommId,npCommId)
gameEboot = gameEboot.replace(gameNpCommSign,npCommSign)

os.makedirs(trophyVPK+"_temp/sce_sys/trophy/"+npCommId+"_00")
open(trophyVPK+"_temp/eboot.bin","wb").write(gameEboot)
shutil.copy(trophyTRP,trophyVPK+"_temp/sce_sys/trophy/"+npCommId+"_00""/TROPHY.TRP")

zip(trophyVPK+"_temp",trophyVPK)
shutil.rmtree(trophyVPK+"_temp")
if trophyFolder != "":
    shutil.rmtree(trophyFolder+"_decrypted")

tkMessageBox.showinfo(title="Done!",message="Done! Patched game created.")
window.destroy()