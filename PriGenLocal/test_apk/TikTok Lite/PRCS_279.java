/*Application Package Name: com.tiktok.lite.go
class PRCS_279 {
/**
X.0Rc;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p0)
    {
        try {
            return p0.getActiveNetworkInfo();
        } catch (android.net.NetworkInfo v0_2) {
            v0_2.printStackTrace();
            return X.1Mw.L();
        }
    }

/**
X.0Rc;LB(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo LB(android.net.ConnectivityManager p3)
    {
        try {
            System.nanoTime();
        } catch (android.net.NetworkInfo v0_19) {
            X.5If.L(v0_19);
            return X.0Rc.L(p3);
        }
        if (X.5uL.L()) {
            if ((X.75K.L()) || (X.5uK.LBL())) {
                if (X.5uL.LB()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.0Rc.L(p3);
                        return X.5uC.L;
                    } else {
                        if (X.5uL.LBL()) {
                            X.5uL.L("cm_net_info", X.0Rc.L(p3).toString(), X.5uC.L.toString());
                        }
                        return X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    return X.0Rc.L(p3);
                }
            } else {
                return X.0Rc.L(p3);
            }
        } else {
            return X.0Rc.L(p3);
        }
    }

/**
X.0Rc;LB(Landroid/content/Context;)Z
*/

    public static boolean LB(android.content.Context p3)
    {
        try {
            int v1_1 = X.0Rc.LB(((android.net.ConnectivityManager) p3.getSystemService("connectivity")));
        } catch (Exception) {
            return 0;
        }
        if ((v1_1 == 0) || ((!v1_1.isAvailable()) || (1 != v1_1.getType()))) {
            return 0;
        } else {
            return 1;
        }
    }


}