# Kellogg Web Application

### Creating a Windows Service

create_service.py is the python script that will be used to create a Windows service to run the
 Kellogg Data Lake Web Application. The following sections will address the pre-requisites and
  the process of running the script.
#### Prerequisites

The following are the pre-requisites in order to run the service creation script - 
<ul>
<li> Adding Python folder path and the Scripts folder path as both User variable and System
 Variable <br>
    Eg: <b>C:\Python36</b> is the Python folder path and <b>C:\Python36\Scripts</b> is the
     Scripts path.  
 </li>
 <li> Copy the file pywintypes.dll from pywin32_system32, which is under <b>site-packages</b>
  folder, to win32 folder.
 </li>
</ul>

## Process of running a service

The following steps are to be followed in order to create a service.

<ol>
<li> Change the current working directory to the project path.</li>
<li> Run the following command in order to create a service. 
    <pre>python create_service.py --startup auto install </pre>
    <p>
        The following command will create a service with the name <b>KelloggWebApplication</b>.
    </p>
<li> In order to start/stop a service, run the following command
     <pre>python create_service.py start</pre>
     <pre>python create_service.py stop</pre>
</li>
<li>
    If there are any issues with the application during startup, we can identify the errors by
     running the service in the debug mode. But, we need to create the service in order to do so.
     <pre>python create_service.py debug</pre>
</li>
<li>
For more usage options, run the following command
<pre>python create_service.py</pre>
</li>
</ol>
