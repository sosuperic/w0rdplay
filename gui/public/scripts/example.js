var Comment = React.createClass({
  rawMarkup: function(s) {
    var md = new Remarkable();
    var rawMarkup = md.render(s);
    return { __html: rawMarkup };
  },

  render: function() {
    var color;
    if (this.props.is_good == 'unknown') {
      color = 'black';
    } else if (this.props.is_good) {
      color = 'green';
    } else {
      color = 'red';
    }
    return (
      <div className="comment">
        <span
          dangerouslySetInnerHTML={this.rawMarkup(this.props.children.toString())}
          style={{color:color, display:'inline-block'}}
        />
        <span
          dangerouslySetInnerHTML={this.rawMarkup(this.props.spaced)}
          style={{display: 'inline-block', paddingLeft:'30px'}}
        />
      </div>
    );
  }
});

var CommentBox = React.createClass({
  loadCommentsFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  handleCommentSubmit: function(comment) {
    var comments = this.state.data;
    // Optimistically set an id on the new comment. It will be replaced by an
    // id generated by the server. In a production application you would likely
    // not use Date.now() for this and would have a more robust system in place.
    comment.is_good = 'unknown';  // Do this so color appears black initially
    comment.id = Date.now();
    var newComments = [comment].concat(comments);
    this.setState({data: newComments});
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: comment,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        this.setState({data: comments});
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadCommentsFromServer();
    setInterval(this.loadCommentsFromServer, this.props.pollInterval);
  },
  updateComments: function(data) {
    this.setState({data: data});
  },
  render: function() {
    return (
      <div className="commentBox">
        <h4 className="title">w0rdplay</h4>
        <div className="commentForm">
          <CommentForm url="/api/analyze_word/" onCommentSubmit={this.handleCommentSubmit} />
        </div>
        <div>
          <div className="commentList">
            <CommentList
              data={this.state.data}
              ref="commentList" />
          </div>
          <div className="candidateBox">
            <h6 className="speechblocks_title">speechblocks words</h6>
            <CandidateBox
              url="/api/speechblocks/get_words"
              updateComments={this.updateComments} />
          </div>
        </div>
      </div>
    );
  }
});

var CandidateBox = React.createClass({
  loadCandidatesFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadCandidatesFromServer();
  },
  updateState: function(data) {
    this.setState({data: data});
  },
  render: function() {
    return (
      <div className="candidateBox">
        <div>
          <CandidateList
            data={this.state.data}
            url={'api/submit_speechblocks_word'}
            updateState={this.updateState}
            updateComments={this.props.updateComments} />
        </div>
      </div>
    );
  }
});

var CandidateList = React.createClass({
  handleClick: function(i, props) {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: {'i': i, 'id': props.data[i].id, 'text': props.data[i].text},
      success: function(data) {
        this.props.updateState(data['speechblocks_words']);
        this.props.updateComments(data['session_words']);
      }.bind(this),
      error: function(xhr, status, err) {
        this.setState({data: comments});
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var dis = this;
    var candidateNodes = this.props.data.map(function(candidate, i) {
      var boundClick = dis.handleClick.bind(dis, i, dis.props);
      return (
        <Candidate
          key={candidate.id}
          onClick={boundClick} >
          {candidate.text}
        </Candidate>
      );
    });
    return (
      <div className="candidateList">
        {candidateNodes}
      </div>
    );
  }
});

var Candidate = React.createClass({
  rawMarkup: function() {
    var md = new Remarkable();
    var rawMarkup = md.render(this.props.children.toString());
    return { __html: rawMarkup };
  },
  render: function() {
    return (
      <div className="candidate">
        <span
          dangerouslySetInnerHTML={this.rawMarkup()}
          onClick={this.props.onClick}
        />
      </div>
    );
  }
});



var CommentList = React.createClass({
  render: function() {
    var commentNodes = this.props.data.map(function(comment) {
      return (
        <Comment key={comment.id} is_good={comment.is_good} spaced={comment.spaced}>
          {comment.text}
        </Comment>
      );
    });
    return (
      <div className="commentList">
        {commentNodes}
      </div>
    );
  }
});

var CommentForm = React.createClass({
  getInitialState: function() {
    return {text: ''};
  },
  handleTextChange: function(e) {
    // console.log(this.props.classify_word_url);
    var text = e.target.value;
    if (text.length > 0) {
      $.ajax({
        url: this.props.url + text,
        type: 'GET',
        success: function(data) {
          this.state.color = data[0] ? 'green' : 'red';
          this.setState(this.state);  // setState to renender
        }.bind(this),
        error: function(xhr, status, err) {
          // this.setState({data: comments});
          console.error(this.props.url, status, err.toString());
        }.bind(this)
      });
    }
    this.setState({text: text});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    var text = this.state.text.trim();
    if (!text) {
      return;
    }
    this.props.onCommentSubmit({text: text});
    this.setState({text: ''});
  },
  render: function() {
    return (
      <form className="commentForm" onSubmit={this.handleSubmit}>
        <input
          type="text"
          placeholder="Type something..."
          value={this.state.text}
          onChange={this.handleTextChange}
          style={{color: this.state.color}}
        />
      </form>
    );
  }
});

ReactDOM.render(
  <CommentBox url="/api/submit_word" pollInterval={2000} />,
  document.getElementById('content')
);
