/*Application Package Name: com.tiktok.lite.go
class PRCS_405 {
/**
X.4KW;L()Z
*/

    public static boolean L()
    {
        android.location.LocationManager v2_1 = ((android.location.LocationManager) X.4KW.L.getValue());
        if (v2_1 == null) {
            return 0;
        } else {
            if ((v2_1.isProviderEnabled("gps")) || (v2_1.isProviderEnabled("network"))) {
                return 1;
            } else {
                return 0;
            }
        }
    }

/**
X.4OM;L(LX/1BB; LX/1A3; LX/1B1;)V
*/

    public final void L(X.1BB p6, X.1A3 p7, X.1B1 p8)
    {
        boolean v0_0 = X.4OL.L(p6);
        if (v0_0) {
            java.util.LinkedHashMap v3_1 = new java.util.LinkedHashMap();
            java.util.Iterator v4 = v0_0.iterator();
            while (v4.hasNext()) {
                boolean v0_5;
                String v2_1 = ((String) v4.next());
                int v1_0 = v2_1.hashCode();
                if (v1_0 == 3649301) {
                    if (!v2_1.equals("wifi")) {
                        v0_5 = 0;
                    } else {
                        v0_5 = X.4Kc.L();
                    }
                } else {
                    if (v1_0 == 1901043637) {
                        if (!v2_1.equals("location")) {
                        } else {
                            v0_5 = X.4KW.L();
                        }
                    } else {
                        if ((v1_0 != 1968882350) || (!v2_1.equals("bluetooth"))) {
                        } else {
                            v0_5 = X.4KU.LB();
                        }
                    }
                }
                v3_1.put(v2_1, Integer.valueOf(v0_5));
            }
            X.27k.L(p7, v3_1, "");
            return;
        } else {
            X.27k.L(p7, -1, "No valid method in params \"data\".", new java.util.LinkedHashMap());
            return;
        }
    }


}