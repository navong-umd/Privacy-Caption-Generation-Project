/*Application Package Name: com.tiktok.lite.go
class PRCS_40 {
/**
X.5V4;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOGhZ4yA1D1evyWVDftl4baj+xa/Ksgh2HURdbsAYz3XUCX3RcLzP+73Iw==");
            com.bytedance.helios.statichook.api.Result v1_0 = v3_1.preInvoke(183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, "android.net.NetworkInfo", v10_1);
        } catch (android.net.NetworkInfo v0_3) {
            v0_3.printStackTrace();
            return X.1Mw.L();
        }
        if (!v1_0.intercept) {
            android.net.NetworkInfo v4_0 = p18.getActiveNetworkInfo();
            v3_1.postInvoke(v4_0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 1);
            return v4_0;
        } else {
            v3_1.postInvoke(0, 183, "android/net/ConnectivityManager", "getActiveNetworkInfo", p18, v9, v10_1, 0);
            return ((android.net.NetworkInfo) v1_0.returnValue);
        }
    }

/**
X.5V4;call()Ljava/lang/Object;
*/

    public final synthetic Object call()
    {
        android.net.ConnectivityManager v3_0 = X.16B.LB.getSystemService("connectivity");
        java.util.Objects.requireNonNull(v3_0, "null cannot be cast to non-null type android.net.ConnectivityManager");
        android.net.ConnectivityManager v3_1 = ((android.net.ConnectivityManager) v3_0);
        try {
            android.net.NetworkInfo v1_1;
            System.nanoTime();
        } catch (String v0_18) {
            X.5If.L(v0_18);
            v1_1 = X.5V4.L(v3_1);
            X.4GL.L.L(v1_1);
            return kotlin.Unit.L;
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.5V4.L(v3_1);
                        v1_1 = X.5uC.L;
                        X.4GL.L.L(v1_1);
                        return kotlin.Unit.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.5V4.L(v3_1).toString(), X.5uC.L.toString());
                        }
                        v1_1 = X.5uC.L;
                        X.4GL.L.L(v1_1);
                        return kotlin.Unit.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v1_1 = X.5V4.L(v3_1);
                    X.4GL.L.L(v1_1);
                    return kotlin.Unit.L;
                }
            } else {
                v1_1 = X.5V4.L(v3_1);
                X.4GL.L.L(v1_1);
                return kotlin.Unit.L;
            }
        } else {
            v1_1 = X.5V4.L(v3_1);
            X.4GL.L.L(v1_1);
            return kotlin.Unit.L;
        }
    }


}