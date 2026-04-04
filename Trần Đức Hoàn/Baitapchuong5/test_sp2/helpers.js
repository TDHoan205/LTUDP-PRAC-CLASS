// Helper functions
function sapXep(mang) {
    for (let i = 0; i < mang.length; i++) {
        for (let j = 0; j < mang.length - 1; j++) {
            if (mang[j] > mang[j + 1]) {
                let tam = mang[j];
                mang[j] = mang[j + 1];
                mang[j + 1] = tam;
            }
        }
    }
    return mang;
}

function timMax(mang) {
    let lon_nhat = mang[0];
    for (let i = 1; i < mang.length; i++) {
        if (mang[i] > lon_nhat) {
            lon_nhat = mang[i];
        }
    }
    return lon_nhat;
}

function giaiThua(n) {
    if (n <= 1) return 1;
    return n * giaiThua(n - 1);
}

module.exports = { sapXep, timMax, giaiThua };
