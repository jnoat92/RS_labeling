%%
close all;
figure; uiopen('Result_002.bmp',1)
pause;
uiopen('imagery_HH_UW_4_by_4_average.png',1)
pause;

cdata_ = cdata;
cdata_(cdata_>50) = 50;
cdata_(cdata_<30) = 29;

for i=1:3
    imshow(cdata_, []);
    imshow(imagery_HH_UW_4_by_4_average, []);
    r  = uint32(getrect);
    % tile = cdata_(r(2):r(2)+r(4), r(1):r(1)+r(3));
    tile = imagery_HH_UW_4_by_4_average(r(2):r(2)+r(4), r(1):r(1)+r(3));
    imshow(tile, []);
    polygon = drawpolygon();
    newmask = createMask(polygon);

    tile = cdata(r(2):r(2)+r(4), r(1):r(1)+r(3));
    tile(newmask) = 255;
    cdata(r(2):r(2)+r(4), r(1):r(1)+r(3)) = tile;
    cdata_ = cdata;
    cdata_(cdata_>50) = 50;
    cdata_(cdata_<30) = 29;
end

imshow(cdata_, []);
imwrite(cdata, 'Result_002.bmp')
clear;
