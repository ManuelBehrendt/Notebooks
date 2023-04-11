# Julia environment for reproducability
# The first time of execution, it installs all necessary packages
# Project environment for reproducability is automatically loaded
# import Pkg; Pkg.instantiate() # install all necessary packages with necessary versions (first time)
Pkg.status() # list of installed packages



using Mera, PyPlot, ColorSchemes, StatsBase, JuliaDB, TimerOutputs

# prep plots
rcParams = PyPlot.PyDict(PyPlot.matplotlib."rcParams")
rcParams["figure.dpi"] = 150
rcParams["savefig.dpi"] = 150

# prep timer
to = TimerOutput();

# number of output, no path needed if executed in simulation folder
info = getinfo(300);

# search for help:

?getinfo

# list the fields of object "info"
propertynames(info)

# better representation
viewfields(info)

# access a single field:
info.gamma

info.boxlen # code unit

namelist(info)

timerfile(info)

viewfields(info.scale)

# access directly (is used internally in all functions for scaling)
# (e.g. value provided in code units -> multiply by scale factor)
info.scale.Msun_pc2



viewfields(info.constants)

info.constants.kB



# get physical time of simulation:
# internal calculation: info.time * info.scale.Myr
ti = gettime(info, :Myr)



sv = storageoverview(info);

sv # Bytes

# loads the full box and all hydro quantities (leaf cells):
# Progressbar argument: show_progress=false/true
# If your RAM is too small reduce to, e.g, lmax=9
gas = gethydro(info);

mem = usedmemory(gas); # can be applied to any object

propertynames(gas) # list fields

viewfields(gas)

# the hydro data is stored in a table:
gas.data

# select a few columns to get a table-view:
# every row corresponds to a cell
select(gas.data, (:level, :rho, :vx, :vy, :vz, :p))

?gethydro

# loads the full box
# in this case only stellar particles (no dm particles availabe)
part = getparticles(info);



# to compare loading time with MERA-files
@timeit to "RAMSES" begin
    @timeit to "hydro"     gas = gethydro(info, verbose=false)
    @timeit to "particles" part = getparticles(info, verbose=false)
end;
to



# AMR structure is associated with all datatypes
viewdata(300);

# similarly to getinfo function
info = infodata(300);



@timeit to "MERA" begin
    @timeit to "hydro"     gas = loaddata(300, :hydro)
    @timeit to "particles" part= loaddata(300, :particles)
end;
to





# default cell size == max resolution
# full box is taken into account
pg  = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], verbose=false);
pgx = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], direction=:x, verbose=false);
pgy = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], direction=:y, verbose=false);

propertynames(pg)

pg.maps

pg.maps_unit



subplot(2,2,1)
    title("z-direction")
    imshow(log10.(pg.maps[:sd])' , origin="lower", extent=pg.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(2,2,2)
    title("y-direction")
    imshow(log10.(pgx.maps[:sd]) , origin="lower", extent=pgx.cextent, cmap="magma")
    #colorbar()
    xlabel("z [kpc]")
    ylabel("y [kpc]")

subplot(2,2,3)
    title("x-direction")
    imshow(log10.(pgy.maps[:sd])' , origin="lower", extent=pgy.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("z [kpc]")

tight_layout()

# project for different resolutions
# here, lmax is not limited to the maximum resolution of the simulation.
# lmax
pg  = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], lmax=5);
imshow(log10.(pg.maps[:sd]'), origin="lower", extent=pg.cextent, cmap="magma")

# effective resolution (related to the boxsize)
pg  = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], res=100);
imshow(log10.(pg.maps[:sd]'), origin="lower", extent=pg.cextent, cmap="magma")

# pixel-size (related to a physicel size)
pg  = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], pxsize=[100., :pc]);
imshow(log10.(pg.maps[:sd]'), origin="lower", extent=pg.cextent, cmap="magma")



msum(gas, :Msun) # gas mass of the full box

# cutout the letter "M"
gas_M = subregion(gas, :cuboid, 
                xrange=[-20,-10],
                yrange=[-5,5],
                zrange=[-2,2],
                center=[:boxcenter],
                range_unit=:kpc);

pg_M  = projection(gas_M, :sd, :Msun_pc2, center=[:boxcenter], verbose=false);
pgx_M = projection(gas_M, :sd, :Msun_pc2, center=[:boxcenter], direction=:x, verbose=false);
pgy_M = projection(gas_M, :sd, :Msun_pc2, center=[:boxcenter], direction=:y, verbose=false);

subplot(2,2,1)
    imshow(log10.(pg_M.maps[:sd])' , origin="lower", extent=pg_M.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(2,2,2)
    imshow(log10.(pgx_M.maps[:sd]) , origin="lower", extent=pgx_M.cextent, cmap="magma")
    #colorbar()
    xlabel("z [kpc]")
    ylabel("y [kpc]")

subplot(2,2,3)
    imshow(log10.(pgy_M.maps[:sd])' , origin="lower", extent=pgy_M.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("z [kpc]")

tight_layout()

msum(gas_M, :Msun) # gas mass of the "M" region



# define a struct for multiple arguments to pass it to a function at once:
myargs_M = ArgumentsType()

viewfields(myargs_M)

myargs_M.xrange=[-20,-10]
myargs_M.yrange=[-5,5]
myargs_M.zrange=[-2,2]
myargs_M.center=[:boxcenter]
myargs_M.range_unit=:kpc

myargs_E = deepcopy(myargs_M)
myargs_E.xrange=[-10,0]

myargs_R = deepcopy(myargs_M)
myargs_R.xrange=[0,10]

myargs_A = deepcopy(myargs_M)
myargs_A.xrange=[10,20];

# verbose(false) # main switch
# check state with call: verbose()

# with myargs the function is better readable
gas_E = subregion(gas, :cuboid, myargs=myargs_E);
gas_R = subregion(gas, :cuboid, myargs=myargs_R);
gas_A = subregion(gas, :cuboid, myargs=myargs_A);


part_M = subregion(part, :cuboid, myargs=myargs_M);
part_E = subregion(part, :cuboid, myargs=myargs_E);
part_R = subregion(part, :cuboid, myargs=myargs_R);
part_A = subregion(part, :cuboid, myargs=myargs_A);

myargs_M.verbose=false
myargs_E.verbose=false
myargs_R.verbose=false
myargs_A.verbose=false

pg_M = projection(gas_M, [:sd,:T], [:Msun_pc2, :K], center=[:boxcenter], myargs=myargs_M);
pg_E = projection(gas_E, [:sd,:T], [:Msun_pc2, :K], center=[:boxcenter], myargs=myargs_E);
pg_R = projection(gas_R, [:sd,:T], [:Msun_pc2, :K], center=[:boxcenter], myargs=myargs_R);
pg_A = projection(gas_A, [:sd,:T], [:Msun_pc2, :K], center=[:boxcenter], myargs=myargs_A);


pp_M = projection(part_M, :sd, :Msun_pc2, center=[:boxcenter], myargs=myargs_M);
pp_E = projection(part_E, :sd, :Msun_pc2, center=[:boxcenter], myargs=myargs_E);
pp_R = projection(part_R, :sd, :Msun_pc2, center=[:boxcenter], myargs=myargs_R);
pp_A = projection(part_A, :sd, :Msun_pc2, center=[:boxcenter], myargs=myargs_A);

subplot(3,4,1)
    imshow(log10.(pg_M.maps[:sd])' , origin="lower", extent=pg_M.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,2)
    imshow(log10.(pg_E.maps[:sd])' , origin="lower", extent=pg_E.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,3)
    imshow(log10.(pg_R.maps[:sd])' , origin="lower", extent=pg_R.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("z [kpc]")

subplot(3,4,4)
    imshow(log10.(pg_A.maps[:sd])' , origin="lower", extent=pg_A.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")



subplot(3,4,5)
    imshow( log10.(pg_M.maps[:T])' , origin="lower", extent=pg_M.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,6)
    imshow( log10.(pg_E.maps[:T])' , origin="lower", extent=pg_E.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,7)
    imshow( log10.(pg_R.maps[:T])' , origin="lower", extent=pg_R.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("z [kpc]")

subplot(3,4,8)
    imshow( log10.(pg_A.maps[:T])' , origin="lower", extent=pg_A.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")


subplot(3,4,9)
    imshow( log10.(pp_M.maps[:sd])' , origin="lower", extent=pp_M.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,10)
    imshow( log10.(pp_E.maps[:sd])' , origin="lower", extent=pp_E.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

subplot(3,4,11)
    imshow( log10.(pp_R.maps[:sd])' , origin="lower", extent=pp_R.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("z [kpc]")

subplot(3,4,12)
    imshow( log10.(pp_A.maps[:sd])' , origin="lower", extent=pp_A.cextent, cmap="magma")
    #colorbar()
    xlabel("x [kpc]")
    ylabel("y [kpc]")

tight_layout()

# calculate gas and particle mass within the regions
massg_M = msum(gas_M, :Msun)
massg_E = msum(gas_E, :Msun)
massg_R = msum(gas_R, :Msun)
massg_A = msum(gas_A, :Msun);

massp_M = msum(part_M, :Msun)
massp_E = msum(part_E, :Msun)
massp_R = msum(part_R, :Msun)
massp_A = msum(part_A, :Msun);




scatter(["M","E","R","A"], [massg_M, massg_E, massg_R, massg_A])
scatter(["M","E","R","A"], [massp_M, massp_E, massp_R, massp_A])
yscale("log")
xlabel("Regions")
ylabel("Mass [Msun]");




# read the unmodified galaxy data
info = getinfo(300,  verbose=false);
gas = gethydro(info, verbose=false,
        xrange=[-8,8], 
        yrange=[-8,8], 
        zrange=[-2,2], 
        center=[:boxcenter], 
        range_unit=:kpc);

pg = projection(gas, :sd, :Msun_pc2, center=[:boxcenter], verbose=false);
sdmap = pg.maps[:sd];

hrange = -1:0.05:3
h = fit(Histogram, log10.(sdmap[:]), hrange)
pdf = h.weights
sd = hrange[1:end-1]

step( sd,  h.weights)
ylim(10,)
yscale("log")
xlabel("log10(Σ) [Msun_pc2]")
ylabel("counts")

# prepare data:
# =============

# surface density
pg = projection(gas, [:sd, :r_cylinder], [:Msun_pc2, :kpc], center=[:boxcenter], verbose=false);
sdmap = pg.maps[:sd]
rmap = pg.maps[:r_cylinder]

# rotation curve
vrot = getvar(gas, :vϕ_cylinder, :km_s, center=[:boxcenter])
r_vrot = getvar(gas, :r_cylinder, :kpc, center=[:boxcenter])
mass = getvar(gas, :mass, center=[:boxcenter]); # mass in each cell in code unit, used for the weighting

# create radial surfacedensity profile
rrange = 0:0.25:10 # binning [kpc]

hsd  = fit(Histogram, rmap[:], weights(sdmap[:]),  rrange )
nhsd = fit(Histogram, rmap[:], rrange )
Σprofile = hsd.weights ./ nhsd.weights # get average
Σradius = rrange[1:end-1];

# create radial vrot profile
rrange = 0:0.25:10 # binning [kpc]

hvrot = fit(Histogram, r_vrot, weights(vrot .* mass),  rrange )
hmass = fit(Histogram, r_vrot, weights( mass),  rrange )
vrot_profile = hvrot.weights ./ hmass.weights # get mass-weighted average
vrot_radius = rrange[1:end-1];

figure(figsize=(9,4))
subplot(1,2,1)
    plot(Σradius, Σprofile)
    yscale("log")
    xlabel("Rdisk [kpc]")
    ylabel("Σ [Msun/pc^2]")

subplot(1,2,2)
    plot(vrot_radius, vrot_profile)
    xlabel("Rdisc [Msun/pc^2]")
    ylabel("Vrot [km/s]")

tight_layout()



getvar()





cmap2 = ColorMap(reverse((ColorSchemes.romaO.colors)))

Temperature = getvar(gas, :T, :K)
nH = getvar(gas, :rho, :nH)
mass = getvar(gas, :mass, :Msun)

Trange = 1:0.02:9
nHrange = -5.5:0.02:2.5

# 2d histogram
hsd = fit(Histogram, (log10.(nH), log10.(Temperature)), weights(mass),  (nHrange, Trange) );
extent = [minimum(hsd.edges[1]), maximum(hsd.edges[1]), minimum(hsd.edges[2]), maximum(hsd.edges[2])];

imshow(log10.(hsd.weights)', origin="lower", interpolation="none", cmap=cmap2, extent=extent)
colorbar(label="log10(mass/pixel) [Msun]")
xlabel("log10(nH/cm^3)")
ylabel("log10(T/K)");

# select the cold gas
mask_density = getvar(gas, :rho, :nH) .> 1e-2 # cm-3
mask_Temp    = getvar(gas, :T, :K) .< 5e2 # K
mask_tot = mask_density .* mask_Temp;

msum(gas, :Msun, mask=mask_tot) # total mass of the masked/selected region

# project the selected region
psd_cold = projection(gas, :sd, :Msun_pc2, mask=mask_tot, verbose=false);
imshow(log10.(psd_cold.maps[:sd])', origin="lower", cmap=cmap2 )
axis("off")

# load data only one time
nH = getvar(gas, :rho, :nH)  
Temp = getvar(gas, :T, :K) 

# prep masked regions
mask_density_h = nH .< 10.
mask_density_l = nH .> 1e-2

mask_Temp_h    =  Temp .< 1e5 # K
mask_Temp_l    =  Temp .> 1e4 # K

# combine all masks
mask_tot = mask_density_h .* mask_density_l .* mask_Temp_h .* mask_Temp_l;

psd_warm = projection(gas, :sd, :Msun_pc2, mask=mask_tot, verbose=false);
imshow(log10.(psd_warm.maps[:sd])', origin="lower", cmap=cmap2 )
axis("off");




