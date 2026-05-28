/*Application Package Name: com.tiktok.lite.go
class PRCS_284 {
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
X.0Rc;L(Landroid/content/Context;)Z
*/

    public static boolean L(android.content.Context p2)
    {
        try {
            int v0_4 = X.0Rc.LB(((android.net.ConnectivityManager) p2.getSystemService("connectivity")));
        } catch (Exception) {
            return 0;
        }
        if ((v0_4 == 0) || (!v0_4.isConnected())) {
            return 0;
        } else {
            return 1;
        }
    }


}