import ROOT, array, math

class PointGenerator:
	def __init__(self, x0=0, y0=0, s=1):
		self.r = ROOT.Math.Random(ROOT.Math.GSLRngMT)()
		self.x0=x0; self.y0=y0; self.s=s;
	
	def setParam(self, x0=0, y0=0, s=1):
		self.x0=x0; self.y0=y0; self.s=s;
	
	def g(self):
		x=ROOT.Double();y=ROOT.Double();
		self.r.Gaussian2D(self.s,self.s,0,x,y)
		return (x+self.x0, y+self.y0)
	
	def createTree(self, treename, stuff):
		x=array.array('f',[0])
		y=array.array('f',[0])
		d2=array.array('f',[0])
		phi=array.array('f',[0])
						
		tree = ROOT.TTree('Events', 'Events')
		
		b_x  = tree.Branch('x', x, 'x/F')
		b_y  = tree.Branch('y', y, 'y/F')
		b_d2 = tree.Branch('d2', d2, 'd2/F')
		b_phi= tree.Branch('phi', phi, 'phi/F')

		for (N, param) in stuff:	
			self.setParam(*param)
			for i in xrange(0,int(N)):
				(x[0],y[0]) = rnd.g()
				d2[0] = x[0]**2 + y[0]**2
				phi[0] = math.atan2(y[0], x[0])
				tree.Fill()

		fout = ROOT.TFile('%s.root'%treename, 'RECREATE')
		trees = fout.mkdir('trees')
		trees.WriteTObject(tree)
		#tree.Draw('x:y')
		fout.Close()
		
		return tree

bg1=(2, 3, 1); bg1_fr=0.6
bg2=(0, 0, 2); bg2_fr=0.4
sig=(4, 0, 1); sig_fr=1.2

evs_bgs=50e3
evs_dat=100e3

rnd = PointGenerator()
t_bg1 = rnd.createTree('bg_uno', [(evs_bgs, bg1)])
t_bg2 = rnd.createTree('bg_dos', [(evs_bgs, bg2)])
t_sig = rnd.createTree('signal', [(evs_bgs, sig)])
t_dat = rnd.createTree('data', [(evs_dat*bg1_fr, bg1), (evs_dat*bg2_fr, bg2), (evs_dat*sig_fr, sig)])
