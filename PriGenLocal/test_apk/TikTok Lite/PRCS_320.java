/*Application Package Name: com.tiktok.lite.go
class PRCS_320 {
/**
X.34L;L(Landroid/net/ConnectivityManager;)Landroid/net/NetworkInfo;
*/

    public static android.net.NetworkInfo L(android.net.ConnectivityManager p18)
    {
        try {
            com.bytedance.helios.statichook.api.HeliosApiHook v3_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v9 = new Object[0];
            com.bytedance.helios.statichook.api.ExtraInfo v10_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Landroid/net/NetworkInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
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
X.34L;L(LX/34w;)LX/34w;
*/

    public final X.34w L(X.34w p25)
    {
        String v4_0 = this.LB;
        try {
            Object[] v11_4;
            System.nanoTime();
        } catch (X.34w v0_17) {
            X.5If.L(v0_17);
            v11_4 = X.34L.L(v4_0);
            String v4_2;
            X.34w v0_18 = p25.LD();
            v0_18.L("sdk-version", android.os.Build$VERSION.SDK_INT);
            v0_18.L("model", android.os.Build.MODEL);
            v0_18.L("hardware", android.os.Build.HARDWARE);
            v0_18.L("device", android.os.Build.DEVICE);
            v0_18.L("product", android.os.Build.PRODUCT);
            v0_18.L("os-uild", android.os.Build.ID);
            v0_18.L("manufacturer", android.os.Build.MANUFACTURER);
            v0_18.L("fingerprint", android.os.Build.FINGERPRINT);
            java.util.Calendar.getInstance();
            v0_18.L().put("tz-offset", String.valueOf(((long) (java.util.TimeZone.getDefault().getOffset(java.util.Calendar.getInstance().getTimeInMillis()) / 1000))));
            if (v11_4 != null) {
                android.content.pm.PackageInfo v6_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                com.bytedance.helios.statichook.api.ExtraInfo v12_0 = new Object[0];
                int v13_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
                com.bytedance.helios.statichook.api.HeliosApiHook v5_0 = v6_1.preInvoke(10216, "android/net/NetworkInfo", "getType", v11_4, v12_0, "int", v13_1);
                if (!v5_0.intercept) {
                    v4_2 = v11_4.getType();
                    v6_1.postInvoke(Integer.valueOf(v4_2), 10216, "android/net/NetworkInfo", "getType", v11_4, v12_0, v13_1, 1);
                } else {
                    v6_1.postInvoke(0, 10216, "android/net/NetworkInfo", "getType", v11_4, v12_0, v13_1, 0);
                    v4_2 = ((Integer) v5_0.returnValue).intValue();
                }
            } else {
                v4_2 = X.34D.NONE.LB;
            }
            String v4_7;
            v0_18.L("net-type", v4_2);
            if (v11_4 != null) {
                android.content.pm.PackageInfo v6_3 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new Object[0];
                int v13_3 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()I", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
                String v4_6 = v6_3.preInvoke(10214, "android/net/NetworkInfo", "getSubtype", v11_4, v12_1, "int", v13_3);
                if (!v4_6.intercept) {
                    v4_7 = v11_4.getSubtype();
                    v6_3.postInvoke(Integer.valueOf(v4_7), 10214, "android/net/NetworkInfo", "getSubtype", v11_4, v12_1, v13_3, 1);
                } else {
                    v6_3.postInvoke(0, 10214, "android/net/NetworkInfo", "getSubtype", v11_4, v12_1, v13_3, 0);
                    v4_7 = ((Integer) v4_6.returnValue).intValue();
                }
                if (v4_7 != -1) {
                    if (X.34C.L(v4_7) == null) {
                        v4_7 = 0;
                    }
                } else {
                    v4_7 = X.34C.COMBINED.L;
                }
            } else {
                v4_7 = X.34C.UNKNOWN_MOBILE_SUBTYPE.L;
            }
            com.bytedance.helios.statichook.api.HeliosApiHook v5_3;
            v0_18.L("mobile-subtype", v4_7);
            Object[] v11_0 = java.util.Locale.getDefault();
            android.content.pm.PackageInfo v6_5 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            com.bytedance.helios.statichook.api.ExtraInfo v12_2 = new Object[0];
            int v13_5 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Ljava/lang/String;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
            com.bytedance.helios.statichook.api.HeliosApiHook v5_2 = v6_5.preInvoke(2885, "java/util/Locale", "getCountry", v11_0, v12_2, "java.lang.String", v13_5);
            if (!v5_2.intercept) {
                v5_3 = v11_0.getCountry();
                v6_5.postInvoke(v5_3, 2885, "java/util/Locale", "getCountry", v11_0, v12_2, v13_5, 1);
            } else {
                v6_5.postInvoke(0, 2885, "java/util/Locale", "getCountry", v11_0, v12_2, v13_5, 0);
                v5_3 = ((String) v5_2.returnValue);
            }
            com.bytedance.helios.statichook.api.HeliosApiHook v5_6;
            v0_18.L("country", v5_3);
            Object[] v11_1 = java.util.Locale.getDefault();
            android.content.pm.PackageInfo v6_7 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            com.bytedance.helios.statichook.api.ExtraInfo v12_3 = new Object[0];
            int v13_7 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Ljava/lang/String;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
            com.bytedance.helios.statichook.api.HeliosApiHook v5_5 = v6_7.preInvoke(2922, "java/util/Locale", "getLanguage", v11_1, v12_3, "java.lang.String", v13_7);
            if (!v5_5.intercept) {
                v5_6 = v11_1.getLanguage();
                v6_7.postInvoke(v5_6, 2922, "java/util/Locale", "getLanguage", v11_1, v12_3, v13_7, 1);
            } else {
                v6_7.postInvoke(0, 2922, "java/util/Locale", "getLanguage", v11_1, v12_3, v13_7, 0);
                v5_6 = ((String) v5_5.returnValue);
            }
            com.bytedance.helios.statichook.api.HeliosApiHook v5_9;
            v0_18.L("locale", v5_6);
            String v9_5 = ((android.telephony.TelephonyManager) this.LBL.getSystemService("phone"));
            String v4_14 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            android.content.pm.PackageManager v10_4 = new Object[0];
            Object[] v11_3 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "()Ljava/lang/String;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
            String v2_0 = v4_14.preInvoke(100917, "android/telephony/TelephonyManager", "getSimOperator", v9_5, v10_4, "java.lang.String", v11_3);
            if (!v2_0.intercept) {
                v5_9 = v9_5.getSimOperator();
                v4_14.postInvoke(v5_9, 100917, "android/telephony/TelephonyManager", "getSimOperator", v9_5, v10_4, v11_3, 1);
            } else {
                v4_14.postInvoke(0, 100917, "android/telephony/TelephonyManager", "getSimOperator", v9_5, v10_4, v11_3, 0);
                v5_9 = ((String) v2_0.returnValue);
            }
            v0_18.L("mcc_mnc", v5_9);
            int v1_11 = this.LBL;
            try {
                android.content.pm.PackageInfo v6_10;
                android.content.pm.PackageManager v10_5 = v1_11.getPackageManager();
                String v3_1 = v1_11.getPackageName();
                com.bytedance.helios.statichook.api.HeliosApiHook v5_13 = new com.bytedance.helios.statichook.api.HeliosApiHook();
                Object[] v11_5 = new Object[2];
                v11_5[0] = v3_1;
                v11_5[1] = Integer.valueOf(0);
                com.bytedance.helios.statichook.api.ExtraInfo v12_8 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;", "dzBzEgU1UM3QUBkgSxaWaaw9Bz50+GPobFdFnURDI6vGJGz7JkgqDVSdRUutPmGhNVjxSSrxjJ0=");
                String v2_3 = v5_13.preInvoke(10054, "android/content/pm/PackageManager", "getPackageInfo", v10_5, v11_5, "android.content.pm.PackageInfo", v12_8);
            } catch (android.content.pm.PackageManager$NameNotFoundException) {
                X.35F.L("CctTransportBackend");
                int v1_16 = -1;
                v0_18.L("application_build", Integer.toString(v1_16));
                return v0_18.LB();
            }
            if (!v2_3.intercept) {
                v6_10 = v10_5.getPackageInfo(v3_1, 0);
                v5_13.postInvoke(v6_10, 10054, "android/content/pm/PackageManager", "getPackageInfo", v10_5, v11_5, v12_8, 1);
            } else {
                v5_13.postInvoke(0, 10054, "android/content/pm/PackageManager", "getPackageInfo", v10_5, v11_5, v12_8, 0);
                v6_10 = ((android.content.pm.PackageInfo) v2_3.returnValue);
            }
            v1_16 = v6_10.versionCode;
            v0_18.L("application_build", Integer.toString(v1_16));
            return v0_18.LB();
        }
        if (X.5uK.LB().L) {
            if ((X.75K.L()) || (X.5uK.LB().LB)) {
                if (X.5uV.L()) {
                    if ((X.5uC.L == null) || ((!X.5uC.L.isConnected()) || (!X.5uC.L.isAvailable()))) {
                        X.5uC.L = X.34L.L(v4_0);
                        v11_4 = X.5uC.L;
                    } else {
                        if (X.5uO.L) {
                            X.5uQ.L("cm_net_info", X.34L.L(v4_0).toString(), X.5uC.L.toString());
                        }
                        v11_4 = X.5uC.L;
                    }
                } else {
                    X.5uC.L = 0;
                    v11_4 = X.34L.L(v4_0);
                }
            } else {
                v11_4 = X.34L.L(v4_0);
            }
        } else {
            v11_4 = X.34L.L(v4_0);
        }
    }


}